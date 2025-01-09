from django.test import TestCase
from usuarios.models import ChatHistory, CustomUser

class ChatHistoryTest(TestCase):
    def test_chat_history_creation(self):
        user = CustomUser.objects.create_user(username='test', password='test123')
        history = ChatHistory.objects.create(
            user=user,
            question="Test Question",
            answer="Test Answer",
        )
        self.assertEqual(history.user.username, 'test')
        self.assertEqual(history.question, "Test Question")
        self.assertEqual(history.answer, "Test Answer")
