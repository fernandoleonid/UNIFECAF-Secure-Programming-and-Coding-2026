// Função para mostrar seções
function showSection(sectionId) {
    // Esconde todas as seções
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.classList.remove('active'));

    // Remove classe active de todos os botões
    const buttons = document.querySelectorAll('.nav-tab');
    buttons.forEach(btn => btn.classList.remove('active'));

    // Mostra a seção selecionada
    document.getElementById(sectionId).classList.add('active');

    // Adiciona classe active ao botão clicado
    event.target.classList.add('active');

    // Scroll para o topo
    window.scrollTo(0, 0);
}

// Sistema de Quiz
let quizAnswers = {};

function checkAnswer(element, isCorrect) {
    const question = element.closest('.quiz-question');
    const questionIndex = Array.from(document.querySelectorAll('.quiz-question')).indexOf(question);
    
    // Remove classes de respostas prévias
    const options = question.querySelectorAll('.quiz-option');
    options.forEach(opt => {
        opt.classList.remove('selected', 'correct', 'incorrect');
    });

    // Adiciona classe apropriada
    if (isCorrect) {
        element.classList.add('correct');
        quizAnswers[questionIndex] = true;
    } else {
        element.classList.add('incorrect');
        quizAnswers[questionIndex] = false;
    }

    element.classList.add('selected');

    // Mostra mensagem
    let resultDiv = question.querySelector('.result-message');
    if (resultDiv) resultDiv.remove();

    const message = document.createElement('div');
    message.className = `result-message ${isCorrect ? 'correct' : 'incorrect'}`;
    message.textContent = isCorrect ? '✅ Correto! Parabéns!' : '❌ Incorreto. Tente novamente ou estude o material.';
    question.appendChild(message);
}

function calculateScore() {
    const totalQuestions = 8;
    const answeredQuestions = Object.keys(quizAnswers).length;

    if (answeredQuestions < totalQuestions) {
        alert('⚠️ Responda todas as 8 questões primeiro!');
        return;
    }

    const correctAnswers = Object.values(quizAnswers).filter(ans => ans === true).length;
    const percentage = Math.round((correctAnswers / totalQuestions) * 100);

    const scoreDisplay = document.getElementById('score-section');
    const scoreNumber = document.getElementById('score-number');
    const scoreLabel = document.getElementById('score-label');

    scoreNumber.textContent = `${correctAnswers}/${totalQuestions}`;
    
    if (percentage === 100) {
        scoreLabel.textContent = '🌟 Excelente! Você domina os conceitos!';
        scoreLabel.style.color = '#10b981';
    } else if (percentage >= 75) {
        scoreLabel.textContent = '✅ Muito bom! Você entendeu bem a maioria dos conceitos!';
        scoreLabel.style.color = '#10b981';
    } else if (percentage >= 50) {
        scoreLabel.textContent = '📚 Bom! Mas revise algumas áreas.';
        scoreLabel.style.color = '#f59e0b';
    } else {
        scoreLabel.textContent = '🔄 Revise o material e tente novamente!';
        scoreLabel.style.color = '#ef4444';
    }

    scoreDisplay.style.display = 'block';
    scoreDisplay.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function resetQuiz() {
    quizAnswers = {};
    document.querySelectorAll('.quiz-option').forEach(opt => {
        opt.classList.remove('selected', 'correct', 'incorrect');
    });
    document.querySelectorAll('.result-message').forEach(msg => msg.remove());
    document.getElementById('score-section').style.display = 'none';
}

// Mostrar primeira seção ao carregar
window.addEventListener('load', () => {
    document.querySelector('.nav-tab').classList.add('active');
});