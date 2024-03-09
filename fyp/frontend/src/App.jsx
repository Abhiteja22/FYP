import './App.css';
import { Routes, Route } from 'react-router-dom';
import Portfolio from './components/Portfolio';
import About from './components/About';
import Create from './components/Create';
import MiniDrawer from './components/NavBar';
import Edit from './components/Edit';
import Delete from './components/Delete';
import CreatePortfolioAsset from './components/CreatePortfolioAsset';
import Chat from './components/Chat';
import Interact from './components/Interact';
import CreateChat from './components/CreateChat';
import EditChat from './components/EditChat';
import Login from './components/Login';
import Register from './components/Register';
import Home from './components/Home';
import MainWrapper from './layouts/MainWrapper';
import PrivateRoute from './layouts/PrivateRoute';
import Private from './components/Private';
import Logout from './components/Logout';

function App() {
  return (
      <MainWrapper>
        <Routes>
          <Route path='/login' element={<Login/>}/>
          <Route path='/register' element={<Register/>}/>
          <Route path='/logout' element={<Logout/>}/>

          <Route path='/private' element={<PrivateRoute> <MiniDrawer content= {<Private/>} /> </PrivateRoute>}/>
          <Route path="/" element={<PrivateRoute> <MiniDrawer content= {<Home/>} /> </PrivateRoute>} />
          <Route path='/portfolio' element={<PrivateRoute> <MiniDrawer content= {<Portfolio/>} /> </PrivateRoute>}/>
          <Route path='/about' element={<PrivateRoute> <MiniDrawer content= {<About/>} /> </PrivateRoute>}/>
          <Route path='/create' element={<PrivateRoute> <MiniDrawer content= {<Create/>} /> </PrivateRoute>}/>
          <Route path='/portfolio/edit/:id' element={<PrivateRoute> <MiniDrawer content= {<Edit/>} /> </PrivateRoute>}/>
          <Route path='/portfolio/delete/:id' element={<PrivateRoute> <MiniDrawer content= {<Delete/>} /> </PrivateRoute>}/>
          <Route path='/createPortfolioAsset' element={<PrivateRoute> <MiniDrawer content= {<CreatePortfolioAsset/>} /> </PrivateRoute>}/>
          <Route path='/chat' element={<PrivateRoute> <MiniDrawer content= {<Chat/>} /> </PrivateRoute>}/>
          <Route path='/chat/create' element={<PrivateRoute> <MiniDrawer content= {<CreateChat/>} /> </PrivateRoute>}/>
          <Route path='/chat/edit/:id' element={<PrivateRoute> <MiniDrawer content= {<EditChat/>} /> </PrivateRoute>}/>
          <Route path='/chat/:chatId' element={<PrivateRoute> <MiniDrawer content= {<Interact/>} /> </PrivateRoute>}/>
        </Routes>
      </MainWrapper>
  );
}

export default App;
