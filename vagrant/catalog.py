from catalog import app
import uuid

app.start_session()
app.secret_key = uuid.uuid4().hex # 'secret_key'
app.run(host='0.0.0.0', port=8000, debug=True)