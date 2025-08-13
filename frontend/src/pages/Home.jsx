import { Link } from "react-router-dom";
import App from "../App.jsx";

export default function Home() {
   return (
      <div>
         <Link to="/app">
            <button>Home</button>
         </Link>
      </div>
   )
}
