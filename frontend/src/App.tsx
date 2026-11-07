import { Navigate, Route, Routes } from 'react-router-dom'
import { auth } from './api'
import Layout from './components/Layout'
import AdminImportPage from './pages/AdminImportPage'
import CustomerPage from './pages/CustomerPage'
import CustomersPage from './pages/CustomersPage'
import GoalsPage from './pages/GoalsPage'
import LoginPage from './pages/LoginPage'
import TransactionsPage from './pages/TransactionsPage'

function Protected(){return auth.token()?<Layout/>:<Navigate to="/login" replace/>}
export default function App(){return <Routes><Route path="/login" element={<LoginPage/>}/><Route element={<Protected/>}><Route path="/customers" element={<CustomersPage/>}/><Route path="/customers/:id" element={<CustomerPage/>}/><Route path="/customers/:id/transactions" element={<TransactionsPage/>}/><Route path="/customers/:id/goals" element={<GoalsPage/>}/><Route path="/admin/import" element={<AdminImportPage/>}/></Route><Route path="*" element={<Navigate to={auth.token()?'/customers':'/login'} replace/>}/></Routes>}
