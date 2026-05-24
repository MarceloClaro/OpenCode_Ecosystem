from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from PyPDF2 import PdfReader
import mimetypes
from dotenv import load_dotenv
from groq import Groq

# Configuração do app
app = Flask(__name__)

app.config['SECRET_KEY'] = '123'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'saas.db')}"
app.config['UPLOAD_FOLDER'] = 'instance/uploads'

# Inicialização do banco de dados e login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Modelos do banco de dados
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)  # Adicionado
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_subscribed = db.Column(db.Boolean, default=False)  # Assinatura

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    job = db.relationship('Job', backref=db.backref('resumes', lazy=True))

# Configuração do login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rotas
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
# Define a rota '/login' que aceita os métodos HTTP 'GET' e 'POST'. 
# Essa rota será usada para exibir o formulário de login (GET) ou processar os dados enviados (POST).

def login():
    # Define a função que será executada quando a rota '/login' for acessada.

    if request.method == 'POST':
        # Verifica se o método da requisição é 'POST', ou seja, se o formulário de login foi enviado.

        email = request.form['email']
        # Obtém o valor do campo 'email' do formulário enviado.

        password = request.form['password']
        # Obtém o valor do campo 'password' do formulário enviado.

        user = User.query.filter_by(email=email).first()
        # Consulta o banco de dados para encontrar o usuário com o e-mail fornecido. 
        # O método 'first()' retorna o primeiro resultado encontrado ou 'None' se não encontrar.

        if user and check_password_hash(user.password, password):
            # Verifica se o usuário foi encontrado no banco de dados e se a senha fornecida é válida. 
            # 'check_password_hash' compara o hash armazenado da senha com a senha fornecida.

            login_user(user)
            # Registra o usuário na sessão utilizando uma função auxiliar, geralmente fornecida por bibliotecas de autenticação como Flask-Login.

            if user.is_subscribed:
                # Verifica se o usuário tem uma assinatura ativa (um atributo booleano armazenado no modelo do usuário).

                return redirect(url_for('dashboard'))
                # Redireciona o usuário para a página de dashboard caso tenha assinatura ativa.

            else:
                return redirect(url_for('subscribe_prompt'))
                # Redireciona o usuário para uma página que solicita a assinatura, caso não seja assinante.

        flash('Credenciais inválidas. Tente novamente.')
        # Exibe uma mensagem de erro ao usuário se o login falhar (usuário não encontrado ou senha incorreta).
        # O 'flash' é usado para passar mensagens de feedback ao frontend.

    return render_template('login.html')
    # Retorna o template 'login.html' para renderização no navegador, 
    # normalmente usado para exibir o formulário de login ou mensagens de erro.



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        # Certifique-se de incluir 'username' na criação do usuário
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Cadastro realizado com sucesso. Faça login.')

        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_subscribed:
        flash("Você precisa concluir a assinatura para acessar o dashboard.")
        return redirect(url_for('subscribe_prompt'))
    jobs = Job.query.all()  # Carregar currículos associados
    return render_template('dashboard.html', jobs=jobs)


@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def manage_jobs():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_job = Job(title=title, description=description)
        db.session.add(new_job)
        db.session.commit()
        flash('Vaga criada com sucesso!')
        return redirect(url_for('manage_jobs'))
    jobs = Job.query.all()
    return render_template('manage_jobs.html', jobs=jobs)


@app.route('/delete_job', methods=['POST'])
@login_required
def delete_job():
    job_id = request.form['job_id']
    job = Job.query.get(job_id)
    if job:
        db.session.delete(job)
        db.session.commit()
        flash('Vaga excluída com sucesso!')
    return redirect(url_for('manage_jobs'))



@app.route('/submit_resume', methods=['GET', 'POST'])
@login_required
def upload_resume():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        job_id = request.form['job_id']
        resume_file = request.files['resume']

        # Salvar o arquivo
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
        resume_file.save(file_path)

        # Criar entrada no banco de dados
        new_resume = Resume(name=name, email=email, file_path=file_path, job_id=job_id)
        db.session.add(new_resume)
        db.session.commit()
        flash('Currículo enviado com sucesso!')
        return redirect(url_for('analyze_resume', resume_id=new_resume.id))  # Redireciona para a análise

    jobs = Job.query.all()
    return render_template('upload_resume.html', jobs=jobs)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém a chave da API do arquivo .env
api_key = os.getenv("GROQ_API_KEY")

# Verifique se a chave foi carregada corretamente (opcional para depuração)
if not api_key:
    raise ValueError("A chave da API OpenAI não foi encontrada. Certifique-se de que o arquivo .env contém a variável GROQ_API_KEY.")

client = Groq(
            api_key=api_key,
        )

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() for page in reader.pages)

@app.route('/analyze_resume/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def analyze_resume(resume_id):
   
    resume = db.session.get(Resume, resume_id)
    if not resume:
        flash('Currículo não encontrado!')
        return redirect(url_for('dashboard'))

    job = resume.job
    try:
        # Detectar e processar o arquivo
        mime_type, _ = mimetypes.guess_type(resume.file_path)
        if mime_type == "application/pdf":
            with open(resume.file_path, 'rb') as file:
                resume_text = extract_text_from_pdf(file)
        elif mime_type.startswith("text/"):
            with open(resume.file_path, 'r', encoding='utf-8') as file:
                resume_text = file.read()
        else:
            flash("Formato de arquivo não suportado. Apenas PDFs e arquivos de texto são aceitos.")
            return redirect(url_for('dashboard'))

        # Limpar formatação do texto
        resume_text = ' '.join(resume_text.split())        

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um assistente de IA especializado em análise de currículos."},
                {
                    "role": "user",
                    "content": f"""
                    Analise o seguinte currículo em relação à vaga descrita. Atribua um score de compatibilidade de 0 a 100 baseado na relevância das habilidades, experiências e qualificações mencionadas.

                    Currículo:
                    {resume_text}

                    Vaga:
                    {job.description}

                    Retorne apenas o score e uma breve justificativa, formatados assim:
                    SCORE: [valor entre 0 e 100]
                    JUSTIFICATIVA: [justificativa breve]
                    """
                }
            ],
            model="llama3-8b-8192",
        )

        print(chat_completion.choices[0].message.content)        

        # Log da resposta do modelo
        analysis_result = chat_completion.choices[0].message.content.strip()
        print("Resposta do modelo:", analysis_result)

        # Processar a resposta do modelo
        for line in analysis_result.split("\n"):
            line = line.strip()
            if line.startswith("SCORE:"):
                try:
                    compatibility_score = int(line.replace("SCORE:", "").strip())
                except ValueError:
                    compatibility_score = 0
            elif line.startswith("JUSTIFICATIVA:"):
                justification = line.replace("JUSTIFICATIVA:", "").strip()

        if compatibility_score is None:
            flash("Erro ao calcular o score de compatibilidade.")
            return redirect(url_for('dashboard'))

    except Exception as e:
        flash(f"Erro durante o processamento: {str(e)}")
        print("Erro durante o processamento:", e)
        return redirect(url_for('dashboard'))

    return render_template(
        'analysis_result.html',
        candidate=resume,
        job=job,
        compatibility_score=compatibility_score,
        analysis_details=f"JUSTIFICATIVA: {justification}".replace("\n", "<br>")
    )


@app.route('/subscribe_prompt')
@login_required
def subscribe_prompt():
    return render_template('subscribe_prompt.html')


@app.route('/success')
@login_required
def success():
    # Atualiza o status do usuário para "assinante"
    current_user.is_subscribed = True
    db.session.commit()
    flash('Assinatura realizada com sucesso! Bem-vindo ao painel!')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Recria as tabelas no banco
    app.run(debug=True)


