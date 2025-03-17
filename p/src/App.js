import React, { useState } from 'react';
import Home from './Home'; // Jib Home component
import Learn from './learn'; // Jib Learn component

function App() {
    const [currentPage, setCurrentPage] = useState('home'); // State bash nshri l-page li bghina

    return (
        <div>
            <h1>Bienvenue f LittleGenius</h1>
            {/* Boutons bash tbdl bin l-pages */}
            <button onClick={() => setCurrentPage('home')}>Dar l-9raya</button>
            <button onClick={() => setCurrentPage('learn')}>Page d’apprentissage</button>

            {/* Shart bash nshri l-page */}
            {currentPage === 'home' ? <Home /> : <Learn />}
        </div>
    );
}

export default App;