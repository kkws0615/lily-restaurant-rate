import streamlit as st
import requests
import time
import random

# --- 網頁介面設定 ---
st.set_page_config(page_title="蝦皮省錢小幫手", page_icon="🛍️")
st.title("🛍️ 蝦皮共同賣家搜尋器")
st.markdown("輸入兩件商品，幫你找出**在同一家店都有賣**的賣家，讓你只付一次運費！")

# --- 核心搜尋函數 ---
def search_shopee(keyword):
    # 模擬真實瀏覽器的標頭，隨機切換 User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Referer": "https://shopee.tw/",
        "x-api-source": "pc",
        "x-shopee-language": "zh-Hant"
    }

    # 蝦皮搜尋 API
    url = f"https://shopee.tw/api/v4/search/search_items?by=relevancy&keyword={keyword}&limit=50&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        data = response.json()
        items = data.get('items', [])
        
        # 整理賣家資料
        seller_results = {}
        for item in items:
            b = item.get('item_basic')
            if b:
                shopid = b['shopid']
                seller_results[shopid] = {
                    "name": b['name'],
                    "price": b['price'] / 100000,
                    "itemid": b['itemid']
                }
        return seller_results
    except Exception as e:
        return None

# --- 前端介面佈局 ---
col1, col2 = st.columns(2)
with col1:
    item_a = st.text_input("搜尋商品 A", placeholder="例如：螢幕保護貼")
with col2:
    item_b = st.text_input("搜尋商品 B", placeholder="例如：手機殼")

if st.button("🔍 開始交叉搜尋"):
    if item_a and item_b:
        with st.spinner("正在努力翻找蝦皮賣場中..."):
            # 搜尋第一件商品
            results_a = search_shopee(item_a)
            # 隨機延遲 1.5 ~ 3 秒，避免被蝦皮偵測為機器人
            time.sleep(random.uniform(1.5, 3.0)) 
            # 搜尋第二件商品
            results_b = search_shopee(item_b)

            if results_a is None or results_b is None:
                st.error("❌ 蝦皮暫時拒絕了請求，請稍等一分鐘後再試。")
            else:
                # 找出兩個搜尋結果中共同的 shopid (賣家 ID)
                common_shops = set(results_a.keys()) & set(results_b.keys())

                if common_shops:
                    st.success(f"🎊 找到了！共有 {len(common_shops)} 個賣家同時販售這兩樣商品。")
                    
                    for shopid in common_shops:
                        with st.expander(f"🏪 賣家 ID: {shopid} (點擊查看詳情)"):
                            st.write(f"✅ **{item_a}**：{results_a[shopid]['name']} (價格: ${results_a[shopid]['price']})")
                            st.write(f"✅ **{item_b}**：{results_b[shopid]['name']} (價格: ${results_b[shopid]['price']})")
                            st.link_button("👉 前往該賣場", f"https://shopee.tw/shop/{shopid}")
                else:
                    st.warning("⚠️ 沒找到同時賣這兩樣的賣家，請試著簡化關鍵字。")
    else:
        st.info("💡 請在上方輸入兩個關鍵字。")

st.caption("註：如果搜尋結果過多，建議增加關鍵字的準確度（例如加上品牌）。")
