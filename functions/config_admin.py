# 引入 Firebase 函數庫
from firebase_admin import initialize_app, credentials, storage

# 初始化 Firebase 應用程式
app = initialize_app(
    credentials.ApplicationDefault(),
    {
        'storageBucket': "accuinbio-suspect-x.firebasestorage.app"
    }
)

# 取得 storage bucket
bucket = storage.bucket(app=app)
