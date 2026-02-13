import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# 1. [디자인] 원노트 감성의 화이트 스타일
st.set_page_config(page_title="청호방재 상세일지", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    /* 원노트 셀 느낌의 컨테이너 */
    .onenote-cell {
        border-left: 5px solid #BBDEFB;
        background-color: #F8F9FA;
        padding: 20px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 20px;
        color: #000000;
    }
    .date-tag { font-weight: bold; color: #0D47A1; font-size: 14px; }
    .cat-tag { 
        background-color: #E3F2FD; padding: 2px 10px; 
        border-radius: 15px; font-size: 12px; margin-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. [데이터 관리] 각 현장별 개별 DB 로드
def load_work_db(site_name):
    filename = f"work_{site_name}.csv"
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=['상담일', '업무분류', '상담내용', '이미지경로'])

# 3. [메인 화면]
site_name = st.session_state.get('selected_site', '공통현장')
st.title(f"🏢 {site_name} 현장 상세기록")

# 상단 업무 분류 참고바 (사장님 요청: 분류표 횡으로 정렬)
st.markdown("---")
cols = st.columns(6)
categories = ["📞 통화", "🚗 방문", "📧 E-메일", "🏗️ 공사", "📄 서류작업", "💰 발행-입금"]
for i, cat in enumerate(categories):
    cols[i].caption(cat)
st.markdown("---")

# 4. [입력 섹션] 글을 쓰면 날짜 자동 생성
with st.container():
    st.subheader("📝 새 업무 기록")
    
    # 상담 내용 입력 (글을 입력하면 작동)
    content = st.text_area("상담 내용을 입력하세요 (원노트처럼 자유롭게 붙여넣기 가능)", height=150)
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        # 내용이 입력되면 오늘 날짜가 기본값, 아니면 수정 가능
        default_date = datetime.now().date()
        counsel_date = st.date_input("📅 상담일", value=default_date)
    
    with col2:
        # 클릭 지점 팝업 대신 가장 직관적인 셀렉트 박스 (클릭 시 옵션 노출)
        work_cat = st.selectbox("🗂️ 업무 분류 선택", categories)
        
    with col3:
        # 사진 업로드
        uploaded_file = st.file_uploader("📸 사진/자료 첨부", type=['png', 'jpg', 'jpeg'])

    if st.button("🚀 현장 기록 추가"):
        if content:
            # 이미지 저장 로직 (실제 운영 시 폴더 생성 필요)
            img_path = ""
            if uploaded_file:
                img_path = f"img_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            # 데이터 저장
            new_data = pd.DataFrame([[counsel_date, work_cat, content, img_path]], 
                                    columns=['상담일', '업무분류', '상담내용', '이미지경로'])
            db = load_work_db(site_name)
            pd.concat([db, new_data]).to_csv(f"work_{site_name}.csv", index=False)
            st.success("기록되었습니다!")
            st.rerun()
        else:
            st.warning("상담 내용을 입력해야 기록이 생성됩니다.")

st.divider()

# 5. [출력 섹션] 원노트식 타임라인 (높이 자동 조절 및 이미지 정렬)
st.subheader("📜 현장 히스토리")
db = load_work_db(site_name)

if not db.empty:
    # 최신순 정렬
    for i, row in db.iloc[::-1].iterrows():
        with st.container():
            # 원노트 셀 디자인 적용
            st.markdown(f"""
                <div class="onenote-cell">
                    <span class="date-tag">🗓️ {row['상담일']}</span>
                    <span class="cat-tag">{row['업무분류']}</span>
                    <div style="margin-top:15px; white-space: pre-wrap; line-height:1.6;">{row['상담내용']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # 이미지가 있을 경우 비율 유지하며 출력
            if pd.notna(row['이미지경로']) and row['이미지경로'] != "":
                if os.path.exists(row['이미지경로']):
                    img = Image.open(row['이미지경로'])
                    st.image(img, caption=f"현장 사진 - {row['상담일']}", use_column_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
else:
    st.info("아직 등록된 기록이 없습니다.")
