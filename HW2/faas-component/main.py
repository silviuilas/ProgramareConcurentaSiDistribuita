import functions_framework
from google.cloud import firestore


db = firestore.Client()
@functions_framework.http
def add_vote(request):
    request_json = request.get_json()
    poll_id = request_json['poll_id']
    document_id = request_json['document_id']
    payload = request_json['payload']
    
    option_doc_ref = db.collection('votes').document(poll_id).collection('options').document(document_id)
    option_doc = option_doc_ref.get()
    if option_doc.exists:
        option_name = option_doc.to_dict()['name']
    else:
        return 'Option not found', 404

    vote_doc_ref = option_doc_ref.collection('vote')
    if validate_vote(vote_doc_ref, payload):
        payload['vote_name'] = option_name
        vote_doc_ref.add(payload)
    else:
        return 'error'

    return 'Vote saved successfully!'

def validate_vote(doc_ref, payload):
    votes = doc_ref.stream()
    for vote in votes:
        vote_data = vote.to_dict()
        if vote_data['ip']==payload['ip']:
            return False
    return True