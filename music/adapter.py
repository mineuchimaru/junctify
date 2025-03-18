from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def add_message(self, request, level, message_template,
                    message_context=None, extra_tags=''):
        # ログイン成功メッセージを抑制（何もしない）
        pass

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def add_message(self, request, level, message_template,
                    message_context=None, extra_tags=''):
        # ソーシャルログイン成功メッセージを抑制（何もしない）
        pass