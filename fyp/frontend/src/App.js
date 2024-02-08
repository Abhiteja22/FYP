import './App.css';
import {Routes, Route} from 'react-router-dom';
import Home from './components/Home';
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

function App() {
  return (
    <div className='App'>
      <MiniDrawer 
        content = {
          <Routes>
            <Route path='' element={<Home/>}/>
            <Route path='/about' element={<About/>}/>
            <Route path='/create' element={<Create/>}/>
            <Route path='/edit/:id' element={<Edit/>}/>
            <Route path='/delete/:id' element={<Delete/>}/>
            <Route path='/createPortfolioAsset' element={<CreatePortfolioAsset/>}/>
            <Route path='/chat' element={<Chat/>}/>
            <Route path='/chat/create' element={<CreateChat/>}/>
            <Route path='/chat/edit/:id' element={<EditChat/>}/>
            <Route path='/chat/:chatId' element={<Interact/>}/>
          </Routes>
        }
      />
    </div>
  );
}

export default App;
