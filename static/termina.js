// Função para executar o código inserido no terminal
function executeCode() {
    const language = document.getElementById('languageSelect').value; // Obtém a linguagem escolhida
    const code = document.getElementById('codeInput').value; // Obtém o código digitado
    const outputElement = document.getElementById('output'); // Área para exibir o resultado

    // Reseta o conteúdo do output antes de executar o código
    outputElement.textContent = '';

    // Simulação de execução com base na linguagem selecionada
    switch (language) {
        case 'python':
            outputElement.textContent = 'Execução de código Python ainda não suportada no frontend.';
            break;
        case 'javascript':
            try {
                // Eval apenas para JavaScript (não use eval em produção sem validação rigorosa)
                const result = eval(code);
                outputElement.textContent = `Resultado:\n${result}`;
            } catch (error) {
                outputElement.textContent = `Erro:\n${error.message}`;
            }
            break;
        case 'java':
        case 'csharp':
        default:
            outputElement.textContent = `Execução para a linguagem ${language} não está implementada no momento.`;
            break;
    }
}

// Listener para o botão de execução
document.getElementById('executeButton').addEventListener('click', executeCode);
