from pathlib import Path
from werkzeug.datastructures import FileStorage

resources = Path(__file__).parent.parent / "resources"

def test_upload(client):

    with open(resources / "testmd.md", "rb") as file:
        file_storage = FileStorage(stream=file, filename="testmd.md", content_type="text/markdown")

        response = client.post(
            "/flashcards/upload",
            data={
                "setName": "test",
                "setDescription": "A test set description",
                "file": file_storage  # Simulating file upload
            },
        )

    print(response.json)
    assert response.status_code == 302

    #TODO test that the set is successfully uploaded into the db
    
def test_edit(client, test_user, test_flashcards):
    with client.session_transaction() as session:
        session['user_id'] = str(test_user['_id'])

    print(test_flashcards['_id'])
    set_id = test_flashcards['_id']
    response = client.put(f'/flashcards/{set_id}/edit', data={
        "setName": "modifiedSet",
        "setDescription": "this set was edited",
        "front": ["new f1", "new b1"],
        "back": ["new f2", "new b2"]
    })

    assert response.status_code == 302

def test_get_all_users_sets_home(client, test_user, test_flashcards):
    with client.session_transaction() as session:
        session['user_id'] = str(test_user['_id'])

    response = client.get('/flashcards/home')
    assert response.status_code == 200

def test_get_all_users_sets_manage(client, test_user, test_flashcards):
    with client.session_transaction() as session:
        session['user_id'] = str(test_user['_id'])

    response = client.get('/flashcards/manage')
    assert response.status_code == 200


