import { ToastContainer } from 'react-toastify';

import {Routes, Route, Navigate}  from 'react-router-dom'
import { ScoreEntry } from './components/ScoreEntryComponent';
import { DailyScores } from './components/DailyScoresComponent';
import { MonthlyPoints } from './components/MonthlyPointsComponent';
import { CardContainer } from './components/CardContainerComponent';
import {Layout} from './components/LayoutComponent'
import { PasswordGate } from './components/PasswordGateComponent';
import { ProtectedRoute } from './components/ProtectedRouteComponent';

function App() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<PasswordGate />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />} >
            <Route index element={<Navigate to="/score" replace/>} />
            <Route element={<CardContainer />} >
              <Route path="/monthly" element={<MonthlyPoints /> } />
              <Route path="/daily" element={<DailyScores />} />
              <Route path="/score" element={<ScoreEntry  />} />
            </Route>
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
