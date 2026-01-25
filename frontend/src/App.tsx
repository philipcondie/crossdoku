import { ToastContainer } from 'react-toastify';

import {Routes, Route}  from 'react-router-dom'
import { ScoreEntry } from './components/ScoreEntryComponent';
import { DailyScores } from './components/DailyScoresComponent';
import { MonthlyPoints } from './components/MonthlyPointsComponent';
import { CardContainer } from './components/CardContainerComponent';
import {Layout} from './components/LayoutComponent'

function App() {
  return (
    <>
      <Routes>
        <Route element={<Layout />} >
          <Route element={<CardContainer />} >
            <Route path="/monthly" element={<MonthlyPoints /> } />
            <Route path="/daily" element={<DailyScores />} />
            <Route path="/score" element={<ScoreEntry playerName='phil' />} />
          </Route>
        </Route>
      </Routes>
      <ToastContainer 
                position="top-center"
                autoClose={3000}
                hideProgressBar={false}
      />
    </>
  )
}

export default App
