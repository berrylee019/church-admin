import streamlit as st
from datetime import date, timedelta
import streamlit.components.v1 as components
import json, copy, base64, re, io, os, urllib.request

st.set_page_config(page_title="남서울전원교회 주보 발행", layout="wide")

# ---------- 비밀번호: Secrets에만 저장 ----------
# Streamlit Cloud > Settings > Secrets:
# APP_PASSWORD = "실제비밀번호"
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
if "cover_img" not in st.session_state:
    st.session_state.cover_img = ""
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
            # 미리보기용으로만 session에 보관. JSON 저장에는 포함하지 않음(용량 때문).
            st.session_state.cover_img = f"data:{up_img.type};base64,{base64.b64encode(up_img.read()).decode()}"
            st.session_state.cover_name = up_img.name
            st.success("표지 사진이 적용됐습니다.")
        if st.session_state.cover_img:
            st.image(st.session_state.cover_img, width=180, caption=st.session_state.cover_name or "현재 표지 사진")
            if st.button("표지 사진 지우기"):
                st.session_state.cover_img = ""; st.session_state.cover_name = ""; st.rerun()
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

def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def row(label, center, who, star=False):
    return f'<tr><td class="l">{"*" if star else ""}{label}</td><td class="c">{center}</td><td class="r">{who}</td></tr>'
prayer_rows = "".join([f'<tr><td>{esc(d)}</td><td>{esc(n)}</td></tr>' for d, n in B["prayers"]])
sermon_body_html = esc(B["sermon_body"]).replace("\n", "<br>")
cover_img_html = f'<img class="cover-img" src="{st.session_state.cover_img}" alt="">' if st.session_state.cover_img else '<div class="cover-placeholder">🌱<br><span>표지 사진 자리</span></div>'

# ===== 핵심 수정: 인쇄용 CSS를 A4 실물 크기(210x297mm)에 정확히 맞춤 =====
html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{esc(B['date_text'])} 주보</title><style>
@page {{ size: A4 landscape; margin: 0; }}
html, body {{ margin:0 !important; padding:0 !important; width:297mm; background:white; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
* {{ box-sizing:border-box; }}
body {{ font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif; color:#111; }}
.sheet {{ width:297mm; height:210mm; padding:0; margin:0; page-break-after:always; break-after:page; overflow:hidden; background:white; }}
.sheet:last-child {{ page-break-after:auto; break-after:auto; }}
.page {{ width:100%; height:100%; display:flex; gap:0; }}
.half {{ flex:1 1 0; min-width:0; border:none; border-right:1px solid #bbb; border-radius:0; padding:7mm 7mm; position:relative; overflow:hidden; background:white; }}
.cover {{ display:flex; flex-direction:column; justify-content:space-between; text-align:center; border:none; padding:7mm 7mm; }}
.top-line {{ display:flex; justify-content:space-between; font-size:10.5px; }}
.church-sub {{ font-size:21px; font-weight:700; }}
.church {{ font-size:44px; font-weight:900; letter-spacing:1px; line-height:1.15; }}
.theme {{ color:#1e4fd8; font-size:24px; font-weight:800; margin-top:4mm; }}
.cover-img {{ width:100%; height:92mm; object-fit:cover; max-height:none; object-fit:contain; margin:7mm auto 0; display:block; }}
.cover-placeholder {{ font-size:72px; margin:10mm 0; color:#888; }}
.cover-placeholder span {{ font-size:12px; }}
.pastors {{ display:flex; justify-content:space-between; font-size:15px; line-height:1.9; text-align:left; }}
.addr {{ text-align:center; font-size:13px; margin-top:3mm; line-height:1.7; }}
h3 {{ text-align:center; font-size:19px; margin:0 0 3mm; }}
.welcome {{ text-align:center; color:#2a2a9a; font-weight:700; line-height:1.6; font-size:13.5px; }}
.news {{ font-size:14px; line-height:1.75; }}
.news ol {{ padding-left:5mm; margin:2mm 0; }}
.news li {{ margin-bottom:2mm; }}
.mini {{ width:74%; margin:2mm auto; border-collapse:collapse; font-size:12.5px; }}
.mini td {{ border-bottom:1px solid #111; padding:1.2mm 2mm; }}
.mini td:first-child {{ width:32%; text-align:center; }}
.donor {{ font-size:12.5px; line-height:1.9; }}
.donor-row {{ display:flex; gap:2mm; }}
.donor-row b {{ flex:0 0 20mm; white-space:nowrap; }}
.donor-row span {{ flex:1; }}
.guide {{ width:100%; border-collapse:collapse; font-size:11.5px; margin-top:1mm; }}
.guide td {{ border:1px solid #999; padding:1mm 2mm; }}
.guide th {{ background:#eee; padding:1mm; }}
.worship-title {{ border:3px solid #111; text-align:center; font-size:31px; font-weight:900; letter-spacing:8px; padding:2mm; margin-bottom:6mm; }}
.worship-head {{ display:flex; justify-content:space-between; font-size:14px; margin-bottom:4mm; }}
.worship table {{ width:100%; border-collapse:collapse; font-size:13.5px; }}
.worship td {{ padding:1.9mm 1mm; }}
.worship .l {{ width:20%; }} .worship .c {{ width:52%; text-align:center; }} .worship .r {{ width:28%; text-align:right; }}
.note {{ position:absolute; bottom:4mm; left:5mm; font-size:11px; }}
.sermon-title {{ text-align:center; font-size:42px; font-weight:900; letter-spacing:12px; }}
.sermon-ref {{ text-align:center; font-size:12px; margin:3mm 0 5mm; }}
.sermon-body {{ font-size:13.5px; line-height:2.0; }}
@media print {{ html, body {{ width:297mm; }} .sheet {{ margin:0; padding:0; }} }}
</style></head><body>
<div class="sheet"><div class="page">
  <div class="half">
    <h3>◍ 교회 소식 ◍</h3>
    <div class="welcome">♡ 주일 예배에 함께하신 귀하신 성도님들을<br>예수님의 이름으로 환영합니다. ♡</div>
    <div class="news"><ol><li>{esc(B['news1'])}</li><li>{esc(B['news2'])}</li><li>{esc(B['news3'])}</li><li>{esc(B['news4'])}</li><li>{esc(B['news5'])}</li></ol></div>
    <h3 style="font-size:15px;">♡ 11월 대표 기도자 ♡</h3>
    <table class="mini">{prayer_rows}</table>
    <h3 style="font-size:15px;">◍ 지난주 헌금하신 분 ◍</h3>
    <div class="donor">
      <div class="donor-row"><b>● 십 일 조 :</b><span>{esc(B['donor_tithe'])}</span></div>
      <div class="donor-row"><b>● 감사헌금 :</b><span>{esc(B['donor_thanks'])}</span></div>
      <div class="donor-row"><b>● 선교헌금 :</b><span>{esc(B['donor_mission'])}</span></div>
      <div class="donor-row"><b>● 주정헌금 :</b><span>{esc(B['donor_sunday'])}</span></div>
    </div>
    <div style="text-align:center; font-size:11px; margin-top:2mm;">&lt;예 배 안 내&gt;</div>
    <table class="guide"><tr><th>주 일 예 배</th><th>일 오전 11시 00분</th></tr>
      <tr><td>●찬양예배</td><td>주 일 오후 2시 00분</td></tr>
      <tr><td>●수요기도회</td><td>수요일 오전 11시 00분</td></tr>
      <tr><td>●금요기도회</td><td>금요일 오전 11시 00분</td></tr>
      <tr><td>●새벽기도회</td><td>매 일 오전 6시 00분</td></tr></table>
  </div>
  <div class="half cover">
    <div class="top-line"><span>{esc(B['issue'])}</span><span>{esc(B['church_founded'])}</span><span>{esc(B['date_text'])}</span></div>
    <div>
      <div class="church-sub">✚ 대한예수교장로회</div>
      <div class="church">남서울전원교회</div>
      <div class="theme">{esc(B['theme_ko'])}({esc(B['theme_en'])})</div>
      {cover_img_html}
    </div>
    <div>
      <div class="pastors"><div>{esc(B['pastor1'])}<br>{esc(B['pastor2'])}</div><div>{esc(B['pastor3'])}<br>{esc(B['elder1'])}<br>{esc(B['elder2'])}</div></div>
      <div class="addr">{esc(B['address'])}<br>{esc(B['phone'])}</div>
    </div>
  </div>
</div></div>
<div class="sheet"><div class="page">
  <div class="half worship">
    <div class="worship-title">주 일 예 배</div>
    <div class="worship-head"><span><u>{esc(B['worship_time'])}</u></span><span>사회자 : {esc(B['leader'])}</span></div>
    <table>
      {row('묵 도', '----------------', esc(B['mukdo']))}
      {row('찬 송', esc(B['hymn1']), esc(B['hymn1_who']), True)}
      {row('성시교독', esc(B['reading'])+'<br><small>'+esc(B['reading_sub'])+'</small>', esc(B['reading_who']), True)}
      {row('신앙고백', esc(B['confession']), esc(B['confession_who']), True)}
      {row('찬 송', esc(B['hymn2']), esc(B['hymn2_who']))}
      {row('기 도', '----------------', esc(B['prayer_name']))}
      {row('성경봉독', '&lt; '+esc(B['bible_text'])+' &gt;<br><small>'+esc(B['bible_page'])+'</small>', esc(B['bible_who']))}
      {row('헌 금', '----------------', esc(B['offering_who']))}
      {row('봉헌기도', '----------------', esc(B['dedication_who']))}
      {row('설 교', '【 '+esc(B['sermon_title'])+' 】', esc(B['sermon_preacher']))}
      {row('찬 송', esc(B['hymn3']), esc(B['hymn3_who']))}
      {row('교회소식', '----------------', esc(B['news_who']))}
      {row('찬 송', esc(B['hymn4']), esc(B['hymn4_who']), True)}
      {row('축 도', '----------------', esc(B['benediction_who']), True)}
    </table>
    <div class="note">* 표는 일어나서</div>
  </div>
  <div class="half">
    <div class="sermon-title">{esc(B['sermon_page_title'])}</div>
    <div class="sermon-ref">{esc(B['sermon_ref'])}</div>
    <div class="sermon-body">{sermon_body_html}</div>
  </div>
</div></div>
</body></html>"""

st.header(f"📄 {B['date_text']} - {B['issue']} 미리보기")
st.caption("미리보기는 화면용으로 축소돼 보입니다. 실제 크기는 다운로드한 HTML을 열었을 때 A4 꽉 차게 나옵니다.")
components.html(html, height=650, scrolling=True)
c1, c2 = st.columns(2)
with c1:
    st.download_button("📥 ① 주보 HTML 다운로드 (인쇄용)", data=html.encode("utf-8"), file_name=f"주보_{B['date_text']}_{B['issue']}.html", mime="text/html", type="primary")
    st.caption("다운로드한 HTML을 열고 Ctrl+P → A4 가로, 여백 없음, 배율 100%로 인쇄하세요.")
with c2:
    # 사진 제외, 글자만 JSON으로 저장 -> 용량 문제 해결
    st.download_button("💾 ② 이번 주 입력값 저장 (글자만, JSON)", data=json.dumps({"bulletin": B, "cover_name": st.session_state.cover_name}, ensure_ascii=False, indent=2), file_name=f"bulletin_{B['date_text']}.json", mime="application/json")
    up = st.file_uploader("📂 지난주 JSON 불러오기", type=["json"], key="json_up")
    if up:
        data = json.loads(up.read().decode("utf-8"))
        st.session_state.bulletin = data.get("bulletin", data)
        st.session_state.cover_name = data.get("cover_name", "")
        st.session_state.cover_img = ""
        st.rerun()
with st.expander("🖨️ 인쇄 설정 - 이 사진처럼 나오게", expanded=True):
    st.write("1) 다운로드한 HTML을 열고 Ctrl+P")
    st.write("2) 용지: A4, 방향: 가로")
    st.write("3) 여백: 없음 / 머리글·바닥글: 끔")
    st.write("4) 배율: 100% / 실제 크기 (용지에 맞게 아님)")
    st.write("5) 배경 그래픽: 켬, 양면: 짧은 쪽으로 뒤집기")
    st.write("→ 가로 A4 한 장에 소식면+표지가 꽉 차게 나옵니다. 접으면 표지가 바깥으로 나와요.")
