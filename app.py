import streamlit as st
from datetime import date, timedelta
import json, copy, re, io, os, urllib.request

st.set_page_config(page_title="남서울전원교회 주보 발행", layout="wide")

# ---------- 비밀번호: Secrets에만 저장 ----------
# Streamlit Cloud > Settings > Secrets: APP_PASSWORD = "실제비밀번호"
def check_password():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if st.session_state.logged_in:
        return True
    st.title("⛪ 남서울전원교회 주보 발행")
    try:
        correct = st.secrets["APP_PASSWORD"]
    except Exception:
        st.error("Secrets에 APP_PASSWORD가 설정되지 않았습니다.")
        st.info('Streamlit Cloud > Settings > Secrets에 APP_PASSWORD = "비밀번호" 를 입력하고 Save를 누르세요.')
        st.stop()
    pw = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        if pw == correct:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")
    st.stop()
check_password()

DEFAULT = {
    "issue": "제2026-45호", "church_founded": "교회이전설립일 2001.7.8.", "date_text": "2026년 11월 8일",
    "theme_ko": "성령의열매:절제", "theme_en": "self-control",
    "pastor1": "원로목사  장 훈 두", "pastor2": "담임목사", "pastor3": "당회장  박 진 석",
    "elder1": "장 로  장 훈 길", "elder2": "이 재 영",
    "address": "서울시 서초구 내곡동 신흥안길 40-61", "phone": "02) 451-9192",
    "news1": "예배 후에 오찬을 즐기시면서 성도의 교제를 나누시기 바랍니다.",
    "news2": "오늘 설교는 장훈두 목사님입니다.",
    "news3": "다음주일은 추수감사절입니다. 설교는 윤건웅 목사님입니다. 추수감사절에 특별히 평소 전도하는 주변의 이웃들을 초청하여 함께 감사예배를 드리면 좋겠습니다.",
    "news4": "어제 교회에서 김장김치를 하셨습니다. 수고해 주신 성도님들께 감사합니다.",
    "news5": "나라와 민족을 위해, 투병중에 계신 성도님들(장미화집사, 김지우어린이)과 교회의 정상화와 부흥을 위해, 비대위원장님을 위해서 기도 바랍니다.",
    "prayers": [["1일", "장훈길 장로"], ["8일", "장훈길 장로"], ["15일", "구태덕 안수집사"], ["23일", "이병서 피택집사"], ["29일", "장훈길 장로"]],
    "donor_tithe": "장미화 장은경 장훈길 장훈두 지희자", "donor_thanks": "구태덕 장은경 장훈두 지희자",
    "donor_mission": "김현숙 김정자 윤건웅 이병서 장미화 장 철", "donor_sunday": "김철주 이금영",
    "worship_time": "오전 11시", "leader": "장훈길장로", "mukdo": "다같이",
    "hymn1": "찬 39 장", "hymn1_who": "다같이", "reading": "교독문 45번", "reading_sub": "< 시편 103편 >", "reading_who": "다같이",
    "confession": "사도신경", "confession_who": "다같이", "hymn2": "찬 254 장", "hymn2_who": "다같이",
    "prayer_name": "장훈길 장로", "bible_text": "마3:8-12, 13:24-30", "bible_page": "(신약 p.3, 21)", "bible_who": "다같이",
    "offering_who": "신청자", "dedication_who": "설교자", "sermon_title": "추수의 계절", "sermon_preacher": "장훈두목사",
    "hymn3": "찬 589 장", "hymn3_who": "다같이", "news_who": "사회자", "hymn4": "찬 620 장", "hymn4_who": "다같이", "benediction_who": "설교자",
    "sermon_page_title": "추수의 계절", "sermon_ref": "<마태복음 3장 8-12절, 13장 24-30절 말씀> 신약 3, 21쪽",
    "sermon_body": """8. 그러므로 회개에 합당한 열매를 맺고
9. 속으로 아브라함이 우리 조상이라고 생각하지 말라 내가 너희에게 이르노니 하나님이 능히 이 돌들로도 아브라함의 자손이 되게 하시리라
10. 이미 도끼가 나무 뿌리에 놓였으니 좋은 열매를 맺지 아니하는 나무마다 찍혀 불에 던져지리라
11. 나는 너희로 회개하게 하기 위하여 물로 세례를 베풀거니와 내 뒤에 오시는 이는 나보다 능력이 많으시니 나는 그의 신을 들기도 감당하지 못하겠노라 그는 성령과 불로 너희에게 세례를 베푸실 것이요
12. 손에 키를 들고 자기의 타작 마당을 정하게 하사 알곡은 모아 곳간에 들이고 쭉정이는 꺼지지 않는 불에 태우시리라
13:24. 예수께서 또 비유로 그들에게 말씀하시되 천국은 좋은 씨를 제 밭에 뿌린 사람과 같으니
25. 사람들이 잘 때에 그 원수가 와서 곡식 가운데 가라지를 덧뿌리고 갔더니
26. 싹이 나고 결실할 때에 가라지도 보이거늘
27. 집 주인의 종들이 와서 말하되 주여 밭에 좋은 씨를 뿌리지 아니하였나이까 그런데 가라지가 어디서 생겼나이까
28. 주인이 이르되 원수가 이렇게 하였구나 종들이 말하되 그러면 우리가 가서 이것을 뽑기를 원하시나이까
29. 주인이 이르되 가만 두라 가라지를 뽑다가 곡식까지 뽑을까 염려하노라
30. 둘 다 추수 때까지 함께 자라게 두라 추수 때에 내가 추수꾼들에게 말하기를 가라지는 먼저 거두어 불사르게 단으로 묶고 곡식은 모아 내 곳간에 넣으라 하리라""",
}
if "bulletin" not in st.session_state:
    st.session_state.bulletin = copy.deepcopy(DEFAULT)
if "cover_bytes" not in st.session_state:
    st.session_state.cover_bytes = None
if "cover_name" not in st.session_state:
    st.session_state.cover_name = ""
B = st.session_state.bulletin

# ---------- 사이드바 ----------
st.sidebar.title("📝 매주 바뀌는 부분만 입력")
with st.sidebar:
    if st.button("➕ 다음 주보로 복사 (날짜 +7일, 호수 +1)"):
        m = re.search(r"(\d+)년\s*(\d+)월\s*(\d+)일", B["date_text"])
        if m:
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3))) + timedelta(days=7)
            B["date_text"] = f"{d.year}년 {d.month}월 {d.day}일"
        n = re.search(r"(\d+)", B["issue"])
        if n:
            B["issue"] = B["issue"].replace(n.group(1), str(int(n.group(1))+1))
        st.rerun()
    if st.button("↩ 11/8 원본으로 되돌리기"):
        st.session_state.bulletin = copy.deepcopy(DEFAULT); st.rerun()
    with st.expander("1️⃣ 표지 (1면) + 표지 사진", expanded=True):
        B["issue"] = st.text_input("호수", B["issue"])
        B["date_text"] = st.text_input("날짜", B["date_text"])
        B["theme_ko"] = st.text_input("표지 제목", B["theme_ko"])
        B["theme_en"] = st.text_input("표지 영문", B["theme_en"])
        up_img = st.file_uploader("🖼️ 표지 가운데 사진 (매주 교체, 가로 사진 권장)", type=["jpg","jpeg","png","webp"], key="cover_up")
        if up_img is not None:
            st.session_state.cover_bytes = up_img.read()
            st.session_state.cover_name = up_img.name
            st.success("표지 사진이 적용됐습니다.")
        if st.session_state.cover_bytes:
            st.image(st.session_state.cover_bytes, width=180, caption=st.session_state.cover_name)
            if st.button("표지 사진 지우기"):
                st.session_state.cover_bytes = None; st.session_state.cover_name = ""; st.rerun()
    with st.expander("2️⃣ 교회 소식 (2면) - 1~5번", expanded=False):
        for i in range(1, 6):
            B[f"news{i}"] = st.text_area(f"{i}. 소식", B[f"news{i}"], height=80, key=f"news{i}")
    with st.expander("3️⃣ 11월 대표기도자", expanded=False):
        new_p = []
        for idx, (d, n) in enumerate(B["prayers"]):
            c1, c2 = st.columns([1, 2])
            d = c1.text_input(f"날짜 {idx+1}", d, key=f"pr_d{idx}")
            n = c2.text_input(f"이름 {idx+1}", n, key=f"pr_n{idx}")
            new_p.append([d, n])
        B["prayers"] = new_p
        if st.button("기도자 행 +1"):
            B["prayers"].append(["", ""]); st.rerun()
        if st.button("기도자 마지막 행 삭제") and B["prayers"]:
            B["prayers"].pop(); st.rerun()
    with st.expander("4️⃣ 지난주 헌금하신 분", expanded=False):
        B["donor_tithe"] = st.text_input("십 일 조", B["donor_tithe"])
        B["donor_thanks"] = st.text_input("감사헌금", B["donor_thanks"])
        B["donor_mission"] = st.text_input("선교헌금", B["donor_mission"])
        B["donor_sunday"] = st.text_input("주정헌금", B["donor_sunday"])
    with st.expander("5️⃣ 주일 예배 (3면)", expanded=False):
        B["leader"] = st.text_input("사회자", B["leader"])
        B["worship_time"] = st.text_input("예배 시간", B["worship_time"])
        B["mukdo"] = st.text_input("묵도", B["mukdo"])
        B["hymn1"] = st.text_input("찬송 1", B["hymn1"])
        B["reading"] = st.text_input("성시교독", B["reading"])
        B["reading_sub"] = st.text_input("성시교독 부제", B["reading_sub"])
        B["confession"] = st.text_input("신앙고백", B["confession"])
        B["hymn2"] = st.text_input("찬송 2", B["hymn2"])
        B["prayer_name"] = st.text_input("기도", B["prayer_name"])
        B["bible_text"] = st.text_input("성경봉독 본문", B["bible_text"])
        B["bible_page"] = st.text_input("성경봉독 쪽수", B["bible_page"])
        B["offering_who"] = st.text_input("헌금", B["offering_who"])
        B["dedication_who"] = st.text_input("봉헌기도", B["dedication_who"])
        B["sermon_title"] = st.text_input("설교 제목", B["sermon_title"])
        B["sermon_preacher"] = st.text_input("설교자", B["sermon_preacher"])
        B["hymn3"] = st.text_input("찬송 3", B["hymn3"])
        B["hymn4"] = st.text_input("찬송 4", B["hymn4"])
        B["benediction_who"] = st.text_input("축도", B["benediction_who"])
    with st.expander("6️⃣ 설교 본문 (4면)", expanded=False):
        B["sermon_page_title"] = st.text_input("4면 큰 제목", B["sermon_page_title"])
        B["sermon_ref"] = st.text_input("4면 본문 표기", B["sermon_ref"])
        B["sermon_body"] = st.text_area("4면 본문 전체", B["sermon_body"], height=400)

# ---------- 진짜 A4 PDF 생성 (브라우저 인쇄 안 씀) ----------
def get_font():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import pathlib
    # 1) 레포에 NanumGothic.ttf가 있으면 그걸 먼저 씀 (가장 확실)
    for cand in ["NanumGothic.ttf", "fonts/NanumGothic.ttf", "/tmp/NanumGothic.ttf"]:
        if os.path.exists(cand):
            try:
                pdfmetrics.registerFont(TTFont("Nanum", cand))
                pdfmetrics.registerFont(TTFont("Nanum-Bold", cand))
                return "Nanum", "Nanum-Bold"
            except Exception:
                pass
    # 2) 없으면 구글 폰트에서 한 번만 다운로드
    try:
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        path = "/tmp/NanumGothic.ttf"
        if not os.path.exists(path):
            urllib.request.urlretrieve(url, path)
        pdfmetrics.registerFont(TTFont("Nanum", path))
        pdfmetrics.registerFont(TTFont("Nanum-Bold", path))
        return "Nanum", "Nanum-Bold"
    except Exception as e:
        st.warning(f"한글 폰트를 불러오지 못했습니다 ({e}). NanumGothic.ttf를 레포에 넣어주세요.")
        return "Helvetica", "Helvetica-Bold"

def build_pdf():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor, black
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase.pdfmetrics import stringWidth
    font, font_b = get_font()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4  # 595 x 842 pt = A4 세로
    BLUE = HexColor("#1E4FD8"); NAVY = HexColor("#2A2A9A")

    def wrap(text, max_w, size, fnt):
        words, lines, cur = str(text).replace("\n", " "), [], ""
        # 한글은 글자 단위로 줄바꿈
        for ch in str(text):
            if ch == "\n":
                lines.append(cur); cur = ""; continue
            if stringWidth(cur + ch, fnt, size) > max_w:
                lines.append(cur); cur = ch
            else:
                cur += ch
        if cur: lines.append(cur)
        return lines

    def draw_wrapped(x, y_top, w, lines, size, fnt, leading, color=black, align="left"):
        c.setFont(fnt, size); c.setFillColor(color)
        y = y_top
        for ln in lines:
            if align == "center":
                c.drawCentredString(x + w/2, y, ln)
            elif align == "right":
                c.drawRightString(x + w, y, ln)
            else:
                c.drawString(x, y, ln)
            y -= leading
        return y

    def panel(x):
        # 점선 둥근 박스 대신 직사각 점선 테두리 (인쇄에서 가장 안정적)
        c.setStrokeColor(black); c.setLineWidth(1.1); c.setDash(2, 2)
        c.roundRect(x, 18*mm, 92*mm, 265*mm, 8*mm, stroke=1, fill=0)
        c.setDash()

    def cover_page_right(x):
        # 표지: 오른쪽 절반
        cx = x; cw = 92*mm
        y = H - 26*mm
        c.setFont(font, 8); c.setFillColor(black)
        c.drawString(cx+4*mm, y, B["issue"])
        c.drawCentredString(cx+cw/2, y, B["church_founded"])
        c.drawRightString(cx+cw-4*mm, y, B["date_text"])
        y -= 18*mm
        c.setFont(font_b, 15); c.drawCentredString(cx+cw/2, y, "✚ 대한예수교장로회"); y -= 10*mm
        c.setFont(font_b, 27); c.drawCentredString(cx+cw/2, y, "남서울전원교회"); y -= 11*mm
        c.setFont(font_b, 15); c.setFillColor(BLUE)
        c.drawCentredString(cx+cw/2, y, f"{B['theme_ko']}({B['theme_en']})"); c.setFillColor(black); y -= 8*mm
        # 표지 사진: 크게, 비율 유지
        if st.session_state.cover_bytes:
            try:
                img = ImageReader(io.BytesIO(st.session_state.cover_bytes))
                iw, ih = img.getSize()
                box_w, box_h = cw-10*mm, 105*mm
                sc = min(box_w/iw, box_h/ih)
                dw, dh = iw*sc, ih*sc
                c.drawImage(img, cx+(cw-dw)/2, y-dh, width=dw, height=dh, preserveAspectRatio=True, mask="auto")
                y -= dh + 6*mm
            except Exception:
                pass
        else:
            c.setFont(font, 36); c.drawCentredString(cx+cw/2, y-12*mm, "🌱")
            c.setFont(font, 8); c.drawCentredString(cx+cw/2, y-18*mm, "표지 사진 자리"); y -= 26*mm
        # 하단 목회자 / 주소: 아래쪽에 고정
        by = 58*mm
        c.setFont(font, 10)
        c.drawString(cx+5*mm, by+10*mm, B["pastor1"]); c.drawRightString(cx+cw-5*mm, by+10*mm, B["pastor3"])
        c.drawString(cx+5*mm, by+4*mm, B["pastor2"]); c.drawRightString(cx+cw-5*mm, by+4*mm, B["elder1"])
        c.drawRightString(cx+cw-5*mm, by-2*mm, B["elder2"])
        c.setFont(font, 9)
        c.drawCentredString(cx+cw/2, by-12*mm, B["address"])
        c.drawCentredString(cx+cw/2, by-17*mm, B["phone"])

    def news_page_left(x):
        cx = x; cw = 92*mm
        y = H - 30*mm
        c.setFont(font_b, 14); c.drawCentredString(cx+cw/2, y, "◍ 교회 소식 ◍"); y -= 8*mm
        c.setFont(font_b, 9); c.setFillColor(NAVY)
        y = draw_wrapped(cx, y, cw, ["♡ 주일 예배에 함께하신 귀하신 성도님들을", "예수님의 이름으로 환영합니다. ♡"], 9, font_b, 12, NAVY, "center")
        c.setFillColor(black); y -= 2*mm
        c.setFont(font, 9.5)
        for i in range(1, 6):
            lines = wrap(f"{i}. {B[f'news{i}']}", cw-8*mm, 9.5, font)
            y = draw_wrapped(cx+4*mm, y, cw-8*mm, lines, 9.5, font, 13)
            y -= 2*mm
        y -= 1*mm
        c.setFont(font_b, 11); c.drawCentredString(cx+cw/2, y, "♡ 11월 대표 기도자 ♡"); y -= 7*mm
        c.setFont(font, 9)
        for d, n in B["prayers"]:
            c.drawCentredString(cx+cw*0.28, y, d); c.drawString(cx+cw*0.45, y, n)
            c.line(cx+8*mm, y-1.5*mm, cx+cw-8*mm, y-1.5*mm); y -= 6*mm
        y -= 2*mm
        c.setFont(font_b, 11); c.drawCentredString(cx+cw/2, y, "◍ 지난주 헌금하신 분 ◍"); y -= 7*mm
        c.setFont(font, 9)
        for label, val in [("● 십 일 조 :", B["donor_tithe"]), ("● 감사헌금 :", B["donor_thanks"]), ("● 선교헌금 :", B["donor_mission"]), ("● 주정헌금 :", B["donor_sunday"])]:
            lines = wrap(val, cw-28*mm, 9, font)
            c.drawString(cx+4*mm, y, label)
            yy = draw_wrapped(cx+28*mm, y, cw-32*mm, lines, 9, font, 12)
            y = yy - 1*mm
        y -= 2*mm
        c.setFont(font, 8); c.drawCentredString(cx+cw/2, y, "<예 배 안 내>"); y -= 6*mm
        c.setFont(font, 8.5)
        for a, b in [("주 일 예 배", "일 오전 11시 00분"), ("●찬양예배", "주 일 오후 2시 00분"), ("●수요기도회", "수요일 오전 11시 00분"), ("●금요기도회", "금요일 오전 11시 00분"), ("●새벽기도회", "매 일 오전 6시 00분")]:
            c.drawString(cx+4*mm, y, a); c.drawRightString(cx+cw-4*mm, y, b); y -= 5.5*mm

    def worship_page_left(x):
        cx = x; cw = 92*mm
        y = H - 32*mm
        c.setStrokeColor(black); c.setLineWidth(1.5); c.rect(cx+4*mm, y-8*mm, cw-8*mm, 10*mm, stroke=1, fill=0)
        c.setFont(font_b, 20); c.drawCentredString(cx+cw/2, y-5*mm, "주 일 예 배"); y -= 14*mm
        c.setFont(font, 10); c.drawString(cx+4*mm, y, B["worship_time"]); c.drawRightString(cx+cw-4*mm, y, f"사회자 : {B['leader']}"); y -= 10*mm
        rows = [
            ("묵 도", "----------------", B["mukdo"], False), ("*찬 송", B["hymn1"], B["hymn1_who"], False),
            ("*성시교독", f"{B['reading']} {B['reading_sub']}", B["reading_who"], False),
            ("*신앙고백", B["confession"], B["confession_who"], False), ("찬 송", B["hymn2"], B["hymn2_who"], False),
            ("기 도", "----------------", B["prayer_name"], False),
            ("성경봉독", f"< {B['bible_text']} > {B['bible_page']}", B["bible_who"], False),
            ("헌 금", "----------------", B["offering_who"], False), ("봉헌기도", "----------------", B["dedication_who"], False),
            ("설 교", f"【 {B['sermon_title']} 】", B["sermon_preacher"], False),
            ("찬 송", B["hymn3"], B["hymn3_who"], False), ("교회소식", "----------------", B["news_who"], False),
            ("*찬 송", B["hymn4"], B["hymn4_who"], False), ("*축 도", "----------------", B["benediction_who"], False),
        ]
        c.setFont(font, 10)
        for label, center, who, _ in rows:
            lines = wrap(center, 38*mm, 10, font)
            c.drawString(cx+4*mm, y, label)
            yy = draw_wrapped(cx+24*mm, y, 38*mm, lines, 10, font, 13, align="center")
            c.drawRightString(cx+cw-4*mm, y, who)
            y = yy - 2*mm
        c.setFont(font, 8); c.drawString(cx+4*mm, 22*mm, "* 표는 일어나서")

    def sermon_page_right(x):
        cx = x; cw = 92*mm
        y = H - 34*mm
        c.setFont(font_b, 26); c.drawCentredString(cx+cw/2, y, B["sermon_page_title"]); y -= 10*mm
        c.setFont(font, 9); c.drawCentredString(cx+cw/2, y, B["sermon_ref"]); y -= 10*mm
        lines = []
        for para in B["sermon_body"].split("\n"):
            lines.extend(wrap(para, cw-8*mm, 9.5, font) or [""])
        draw_wrapped(cx+4*mm, y, cw-8*mm, lines, 9.5, font, 15)

    # A4 1장: 왼쪽=소식(2면), 오른쪽=표지(1면)
    panel(10*mm); panel(108*mm)
    news_page_left(10*mm); cover_page_right(108*mm)
    c.showPage()
    # A4 2장: 왼쪽=예배(3면), 오른쪽=본문(4면)
    panel(10*mm); panel(108*mm)
    worship_page_left(10*mm); sermon_page_right(108*mm)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

st.header(f"📄 {B['date_text']} - {B['issue']} 미리보기")
st.caption("이제 브라우저 인쇄를 쓰지 않습니다. 아래 PDF 다운로드 버튼으로 받은 PDF를 그대로 인쇄하세요.")
c1, c2 = st.columns(2)
with c1:
    pdf_bytes = build_pdf()
    st.download_button("📥 주보 PDF 다운로드 (A4 2장, 진짜 PDF)", data=pdf_bytes, file_name=f"주보_{B['date_text']}_{B['issue']}.pdf", mime="application/pdf", type="primary")
    st.caption("다운로드한 PDF를 열어서 바로 인쇄하면 됩니다.")
with c2:
    st.download_button("💾 입력값 저장 (글자만, JSON)", data=json.dumps({"bulletin": B, "cover_name": st.session_state.cover_name}, ensure_ascii=False, indent=2), file_name=f"bulletin_{B['date_text']}.json", mime="application/json")
    up = st.file_uploader("📂 지난주 JSON 불러오기", type=["json"], key="json_up")
    if up:
        data = json.loads(up.read().decode("utf-8"))
        st.session_state.bulletin = data.get("bulletin", data)
        st.session_state.cover_name = data.get("cover_name", "")
        st.session_state.cover_bytes = None
        st.rerun()

with st.expander("🖨️ PDF 인쇄 설정 - 딱 이것만", expanded=True):
    st.write("1) 다운로드한 PDF를 엽니다. (크롬/엣지/아크로뱃 아무거나)")
    st.write("2) 인쇄 → 용지: A4, 방향: 세로")
    st.write("3) 크기: 실제 크기 / 100% (절대로 '용지에 맞게', '가로' 선택하지 마세요)")
    st.write("4) 양면: 짧은 쪽으로 뒤집기 → 접으면 표지-소식-예배-본문 순서가 됩니다.")
    st.write("※ 가로 + 용지에 맞게를 누르면 세로 PDF를 가로 용지에 맞추려고 작아지는 게 정상입니다. 그 설정이 원인이었어요.")
