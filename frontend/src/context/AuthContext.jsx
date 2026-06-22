import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('mise_token'))
  const [user, setUser] = useState(() => localStorage.getItem('mise_user'))

  const login = (accessToken, email) => {
    localStorage.setItem('mise_token', accessToken)
    localStorage.setItem('mise_user', email)
    setToken(accessToken)
    setUser(email)
  }

  const logout = () => {
    localStorage.removeItem('mise_token')
    localStorage.removeItem('mise_user')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
