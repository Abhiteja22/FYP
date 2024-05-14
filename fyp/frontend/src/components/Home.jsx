import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/auth';
import Login from './authentication/Login';
import { alignProperty } from '@mui/material/styles/cssUtils';

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
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            width: '100vw', // Ensure the container takes the full viewport width
            position: 'absolute', // Ensures that the flex container is positioned relative to the viewport
            top: 0,
            left: 0
        }}>
            <div>
            <h1>Welcome to Riment</h1>
            <h3>Click on the links to navigate to other pages</h3>
            
            </div>
        </div>
    );
};

export default Home;