import { useEffect } from 'react';
import { api } from './services/api/api';

function Test() {
  useEffect(() => {
    async function testAPI() {
      try {
        console.log('Testing API calls...');

        const players = await api.getPlayers();
        console.log('Players: ', players);

        const games = await api.getGames('phil');
        console.log('Games:', games);

        const scores = await api.getScores({startDate:'2025-12-01'});
        console.log('Scores:', scores);

        const combinedScores = await api.getCombinedScores('2025-12-01');
        console.log('Combined Scores:', combinedScores);

        const monthlyScores = await api.getMonthlyScores('2025-12-25');
        console.log('Monthly Scores:', monthlyScores);

      } catch (error) {
        console.error('API Error: ', error)
      }
    }

    testAPI();
    
  }, []);

  const submitScore = async () => {
    try {
      console.log('Submitting score...');
      const newScore = await api.createScore({gameName:'Sudoku', playerName:'phil', date:'2025-12-28', score:24});
      console.log('New Score:', newScore);
    } catch (error) {
      console.error('Error: ', error);
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Testing API - Check Console</h1>
      <p>Open browser DevTools (F12) and look at the Console tab</p>
      <button
        onClick={submitScore}
      >
        Submit Score
      </button>
    </div>
  );
}

export default Test
