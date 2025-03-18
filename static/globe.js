console.log('Script globes.js carregado'); // Log para verificar se o script foi carregado

function adminLogin() {
    const passwordInput = document.getElementById('adminPassword');
    const password = passwordInput.value.trim();
    passwordInput.value = ''; // Limpa o campo de senha após a tentativa

    if (password === '006698') {
        document.getElementById('adminLogin').style.display = 'none';
        document.getElementById('adminPanel').style.display = 'block';
        initializeEditors();
        document.querySelectorAll('.admin-only').forEach(btn => btn.style.display = 'inline-block');
    } else {
        alert('Senha incorreta!');
    }
}

function initializeEditors() {
    const editors = ['css', 'js', 'html', 'py'];
    editors.forEach(type => {
        const filePath = getFilepath(type);
        if (!filePath) {
            console.error(`Tipo de arquivo inválido: ${type}`);
            return;
        }

        fetch(`/code/${filePath}`)
            .then(response => {
                if (!response.ok) throw new Error('Erro ao carregar arquivo');
                return response.text();
            })
            .then(content => {
                ace.edit(`${type}Editor`, {
                    mode: getMode(type),
                    theme: "ace/theme/monokai",
                    value: content
                });
            })
            .catch(error => console.error('Erro ao inicializar editor:', error));
    });
}

function getFilepath(type) {
    const paths = {
        'css': 'static/style.css',
        'js': 'static/script.js',
        'html': 'templates/index.html',
        'py': 'app.py'
    };
    return paths[type] || ''; // Retorna o caminho ou vazio para tipos inválidos
}

function getMode(type) {
    const modes = {
        'css': 'ace/mode/css',
        'js': 'ace/mode/javascript',
        'html': 'ace/mode/html',
        'py': 'ace/mode/python'
    };
    return modes[type] || 'ace/mode/text'; // Retorna modo de texto para tipos inválidos
}

function confirmChange(editorType) {
    const content = ace.edit(editorType + 'Editor').getValue();

    axios.post('/update-content', {
        type: editorType,
        content: content,
        password: '006698' // ⚠️ Remova a senha do cliente em produção
    })
    .then(() => {
        if (editorType === 'html') location.reload();
        alert('Alterações salvas!');
    })
    .catch(error => {
        console.error('Erro ao salvar alterações:', error);
        alert('Erro ao salvar alterações. Tente novamente.');
    });
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Função de criação de novas seções e páginas otimizada
function addNewSection() {
    const sectionName = prompt('Nome da nova seção:').trim();
    if (sectionName) {
        const newSection = `
            <section class="secao dynamic-section">
                <h2>${escapeHtml(sectionName)}</h2>
                <div class="grid">
                    <div class="project">
                        <h3>Novo Projeto</h3>
                        <pre><code>// Código aqui</code></pre>
                    </div>
                </div>
            </section>
        `;
        document.querySelector('.container').insertAdjacentHTML('beforeend', newSection);
        saveDynamicContent(newSection);
    }
}
