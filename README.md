# FlowerShop Django API + Template

FlowerShop v1 後端與前端系統，使用 Django + Django REST Framework + drf-spectacular + Django Template + Bootstrap 5。

## 技術棧
- Python 3.11+
- Django
- Django REST Framework
- drf-spectacular (Swagger/OpenAPI)
- Bootstrap 5 (RWD)
- SQLite (開發環境)

## 專案結構
- `accounts/`: 會員註冊、登入、會員資料
- `catalog/`: 商品、分類
- `orders/`: 訂單與訂單明細
- `web/`: Django Template 前端頁面（Bootstrap + RWD）
- `common/`: 共用模型
- `static/css/site.css`: 前端樣式
- `media/products/`: 商品圖片上傳位置
- `docs/images/`: README 與專案文件示意圖

## 快速啟動
```bash
cd FlowerShop
py -m venv venv
.venv\Scripts\activate #windows
pip install django
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 重要網址
- 前台商品首頁: `http://127.0.0.1:8000/`
- 前台登入: `http://127.0.0.1:8000/login/`
- 前台註冊: `http://127.0.0.1:8000/register/`
- 我的訂單: `http://127.0.0.1:8000/orders/`
- API Root(JSON): `http://127.0.0.1:8000/api/`
- Swagger UI: `http://127.0.0.1:8000/swagger/`
- OpenAPI Schema: `http://127.0.0.1:8000/api/schema/`
- ReDoc: `http://127.0.0.1:8000/redoc/`
- Django Admin: `http://127.0.0.1:8000/admin/`

## 前台功能（Template）
- 註冊/登入/登出
- 商品列表（支援分類篩選、關鍵字搜尋、分頁）
- 商品詳情與下單
- 我的訂單列表、訂單詳情
- 權限控管：未登入不可下單或查詢訂單

## API 路由
- Auth
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `GET /api/v1/auth/me`
- Catalog
  - `GET/POST /api/v1/categories/`
  - `GET/PUT/PATCH/DELETE /api/v1/categories/{id}/`
  - `GET/POST /api/v1/products/`
  - `GET/PUT/PATCH/DELETE /api/v1/products/{id}/`
- Orders
  - `GET/POST /api/v1/orders/`
  - `GET/PUT/PATCH/DELETE /api/v1/orders/{id}/`

## 圖片與靜態資源規範
- 商品圖片放置於：`/FlowerShop/media/products/`
- 文件示意圖放置於：`/FlowerShop/docs/images/`
- 前端 CSS：`/FlowerShop/static/css/site.css`
- 建議命名：`product_<id>_<short-name>.jpg`

## RWD 驗收建議
請用瀏覽器 DevTools 觀察以下寬度：
- `375px`：手機，確認導覽列、商品卡、訂單列表卡片化呈現
- `768px`：平板，確認格線斷點與表單可用
- `1280px`：桌機，確認雙欄詳情頁與表格版面

## 常見問題
- 無法匯入 Django: 確認已 `source .venv/bin/activate` 並安裝 `requirements.txt`
- 資料表不存在: 先執行 `python manage.py migrate`
- 圖片顯示失敗: 確認 `MEDIA_URL=/media/`、`MEDIA_ROOT=<project_root>/media`，並以 `DEBUG=True` 啟動開發伺服器