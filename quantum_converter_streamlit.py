
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="토스 → 퀀텀 주문 변환기", layout="centered")

st.title("📦 토스 → 퀀텀 주문 변환기 (웹버전)")

# 입력 필드
sender = st.text_input("송하인", value="전국농가자랑")
sender_phone = st.text_input("송하인 연락처", value="010-4429-1245")
keyword = st.text_input("키워드 (옵션명)", value="")

uploaded_file = st.file_uploader("토스 주문서 엑셀 업로드", type=["xlsx"])

converted_df = None

if uploaded_file and keyword and sender and sender_phone:
    try:
        df = pd.read_excel(uploaded_file)
        m_col = df.columns[12]
        filtered_df = df[df[m_col].astype(str).str.contains(keyword)].copy().reset_index(drop=True)

        if len(filtered_df) == 0:
            st.warning("⚠️ 키워드에 해당하는 주문이 없습니다.")
        else:
            # 송하인 정보 삽입
            filtered_df["송하인"] = sender
            filtered_df["송하인 연락처"] = sender_phone

            # 퀀텀 양식으로 재배열
            converted_df = pd.DataFrame()
            converted_df["송하인"] = filtered_df["송하인"]
            converted_df["송하인 연락처"] = filtered_df["송하인 연락처"]
            converted_df["수취인"] = filtered_df["Unnamed: 5"]
            converted_df["수취인 연락처"] = filtered_df["Unnamed: 8"]
            converted_df["우편번호"] = filtered_df["Unnamed: 7"]
            converted_df["주소"] = filtered_df["Unnamed: 6"]
            converted_df["상품명"] = filtered_df["Unnamed: 12"]
            converted_df["수량"] = filtered_df["Unnamed: 14"]
            converted_df["배송 메세지"] = filtered_df["Unnamed: 9"]

            st.success(f"✅ 총 {len(converted_df)}건의 주문이 감지되었습니다.")
            st.dataframe(converted_df.head())

            # 다운로드
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                return output.getvalue()

            st.download_button(
                label="📥 퀀텀주문서 다운로드",
                data=to_excel(converted_df),
                file_name="퀀텀주문서.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"오류 발생: {e}")
else:
    st.info("👆 엑셀 파일, 키워드, 송하인 정보를 모두 입력해주세요.")
