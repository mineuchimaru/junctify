import os
import django_on_heroku
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # 環境変数を読み込む

BASE_DIR = Path(__file__).resolve().parent.parent
USE_S3 = os.getenv('USE_S3', 'True') == 'True'

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-default-secret-key')
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'music',  # allauth より前に移動
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# カスタムユーザーモデル
#AUTH_USER_MODEL = 'music.User'

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SITE_ID = 1

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_SECRET_KEY = os.getenv('GOOGLE_SECRET_KEY')

# Google OAuth 2.0設定
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_SECRET_KEY,
            'key': '',
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'select_account',
        }
    }
}

SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True
# ホストベースの Site 選択を無効化
SOCIALACCOUNT_STORE_TOKENS = True
# デフォルトの Site を強制
SITE_ID = 1

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
# ACCOUNT_LOGOUT_REDIRECT_URL = '/'  # コメントアウトしてカスタムビューに依存
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'
#ACCOUNT_SIGNUP_FORM_CLASS = 'music.forms.CustomSignupForm'
ACCOUNT_LOGOUT_ON_GET = True  # GETリクエストでログアウトを許可
ACCOUNT_LOGIN_METHODS = {'email'}  # 確認用に再記載

# カスタムアダプター（ログイン成功メッセージ非表示用）
ACCOUNT_ADAPTER = 'music.adapter.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'music.adapter.CustomSocialAccountAdapter'

ROOT_URLCONF = 'juncbox.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 空に戻す
        'APP_DIRS': True,  # デフォルトに戻す
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.csrf',  # CSRFトークン用
            ],
        },
    },
]

WSGI_APPLICATION = 'juncbox.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    # 中略
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tokyo'  # 日本時間
USE_I18N = True
USE_TZ = True  # タイムゾーンサポートを有効

# 既存の静的ファイル設定（確認用）
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# STATIC_ROOT を追加
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# S3設定
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'juncbox-music-files')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_FILE_OVERWRITE = False  # ファイルの上書きを防ぐ
AWS_DEFAULT_ACL = 'public-read'  # アップロードしたファイルのアクセス許可
AWS_QUERYSTRING_AUTH = False  # URLに認証情報を含めない
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

# メール設定（開発環境用）
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # コンソールに出力
# 本番環境用（必要に応じてコメント解除）
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'

# セッション設定
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # 開発中はFalse、本番ではTrue
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # セッションをデータベースに保存
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # ブラウザを閉じてもセッションを保持
SESSION_COOKIE_AGE = 1209600  # セッションの有効期限（2週間）