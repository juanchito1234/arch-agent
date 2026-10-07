from chat import repository


def initialize_chat():
    repository.init_db()


def get_sessions():
    return repository.get_all_sessions()


def create_new_session(title="Nueva Sesión"):
    return repository.create_session(title)


def delete_session(session_id):
    repository.delete_session(session_id)


def get_session_messages(session_id):
    return repository.get_messages(session_id)


def add_message(session_id, role, content):
    repository.save_message(
        session_id,
        role,
        content
    )


def update_session_title(session_id, title):
    repository.update_session_title(
        session_id,
        title
    )


def generate_session_title(user_input, max_length=30):
    title = user_input.strip()

    if len(title) > max_length:
        return title[:max_length] + "..."

    return title