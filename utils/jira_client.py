import os
from jira import JIRA, JIRAError
from config import EMOJIS

class JiraClient:
    def __init__(self):
        self.server = os.getenv('JIRA_SERVER')
        self.email = os.getenv('JIRA_EMAIL')
        self.api_token = os.getenv('JIRA_API_TOKEN')
        self.project_key = os.getenv('JIRA_PROJECT_KEY')
        self.client = None
        self._connect()

    def _connect(self):
        """Встановлює з'єднання з Jira"""
        try:
            self.client = JIRA(
                server=self.server,
                basic_auth=(self.email, self.api_token)
            )
        except JIRAError as e:
            print(f"Помилка підключення до Jira: {e}")
            self.client = None

    def is_connected(self):
        """Перевіряє, чи встановлено з'єднання з Jira"""
        return self.client is not None

    def get_my_issues(self):
        """Отримує завдання проекту"""
        if not self.is_connected():
            return f"{EMOJIS['error']} Не вдалося підключитися до Jira"

        try:
            issues = self.client.search_issues(
                f'project = {self.project_key} AND status = "TO DO" ORDER BY updated DESC',
                maxResults=10
            )
            
            if not issues:
                return "\u274C Немає завдань у вашому проекті Jira."

            response = [f"{EMOJIS['task']} *Завдання проекту:*\n"]
            response = [f"{EMOJIS['task']} *Ваші завдання:*\n"]
            for issue in issues:
                status = issue.fields.status.name
                priority = issue.fields.priority.name if hasattr(issue.fields, 'priority') and issue.fields.priority else 'Не вказано'
                
                response.append(
                    f"*{issue.key}* - {issue.fields.summary}\n"
                    f"Статус: *{status}* | Пріоритет: *{priority}*\n"
                    f"[Відкрити в Jira]({self.server}/browse/{issue.key})\n"
                )

            return '\n'.join(response)

        except JIRAError as e:
            return f"{EMOJIS['error']} Помилка при отриманні завдань: {e.text}"

    def create_issue(self, summary, description, issue_type='Task'):
        """Створює нове завдання"""
        if not self.is_connected():
            return f"{EMOJIS['error']} Не вдалося підключитися до Jira"

        try:
            issue_dict = {
                'project': {'key': self.project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type},
            }
            
            issue = self.client.create_issue(fields=issue_dict)
            return (
                f"{EMOJIS['success']} Завдання створено!\n"
                f"*{issue.key}* - {issue.fields.summary}\n"
                f"[Відкрити в Jira]({self.server}/browse/{issue.key})"
            )
            
        except JIRAError as e:
            return f"{EMOJIS['error']} Помилка при створенні завдання: {e.text}"

# Глобальний екземпляр клієнта Jira
jira_client = JiraClient()
