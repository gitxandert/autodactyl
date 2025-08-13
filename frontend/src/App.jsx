import { BrowserRouter as Router } from "react-router-dom";
import AppRoutes from "./routes.jsx";

export default function App() {
   return (
      <Router>
         <AppRoutes />
      </Router>
   );
}
