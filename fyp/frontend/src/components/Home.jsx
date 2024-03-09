import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/auth';
import Login from './Login';

const Home = () => {
    const [isLoggedIn, user] = useAuthStore((state) => [
        state.isLoggedIn,
        state.user,
    ]);
    return (
        <div>
            {isLoggedIn() ? <LoggedInView user={user()} /> : <Login />}
        </div>
    );
};

const LoggedInView = ({ user }) => {
    return (
        <div>
            <h1>Welcome {user.username}</h1>
            <Link to="/private">
                <button>Private</button>
            </Link>
            <Link to="/logout">
                <button>Logout</button>
            </Link>
        </div>
    );
};

export default Home;