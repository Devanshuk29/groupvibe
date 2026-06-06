import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Preferences from './pages/Preferences'
import WaitingRoom from './pages/WaitingRoom'
import Results from './pages/Results'
import PlaceDetails from './pages/PlaceDetails'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/session/:sessionId" element={<WaitingRoom />} />
        <Route path="/join/:sessionId" element={<Preferences />} />
        <Route path="/results/:sessionId" element={<Results />} />
        <Route path="/place/:placeId" element={<PlaceDetails />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
