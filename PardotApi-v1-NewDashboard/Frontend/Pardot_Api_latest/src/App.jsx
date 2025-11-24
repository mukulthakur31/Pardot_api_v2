import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import EmailModule from './components/EmailModule'
import FormsModule from './components/FormsModule'
import ProspectsModule from './components/ProspectsModule'
import LandingPagesModule from './components/LandingPagesModule'
import EngagementModule from './components/EngagementModule'
import UTMModule from './components/UTMModule'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />}>
          <Route index element={<EmailModule />} />
          <Route path="emails" element={<EmailModule />} />
          <Route path="forms" element={<FormsModule />} />
          <Route path="prospects" element={<ProspectsModule />} />
          <Route path="landing-pages" element={<LandingPagesModule />} />
          <Route path="engagement" element={<EngagementModule />} />
          <Route path="utm" element={<UTMModule />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App