import React, { useState, useCallback, createContext, useContext } from "react";
import {
  login as apiLogin,
  register as apiRegister,
  default as api,
} from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem("token");
    if (!token) return null;
    return {
      banker_id: localStorage.getItem("banker_id"),
      banker_name: localStorage.getItem("banker_name"),
      email: localStorage.getItem("email"),
      branch_code: localStorage.getItem("branch_code"),
    };
  });

  const [token, setToken] = useState(localStorage.getItem("token"));
  const [loading, setLoading] = useState(false);

  const login = useCallback(async (emailInput, password) => {
    setLoading(true);
    try {
      const res = await apiLogin(emailInput, password);
      const data = res.data;

      localStorage.setItem("token", data.token);
      localStorage.setItem("banker_id", data.banker_id);
      localStorage.setItem("banker_name", data.banker_name);
      localStorage.setItem("email", data.email);
      localStorage.setItem("branch_code", data.branch_code || "");

      setToken(data.token);
      setUser({
        banker_id: data.banker_id,
        banker_name: data.banker_name,
        email: data.email,
        branch_code: data.branch_code,
      });

      return true;
    } catch (err) {
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(
    async (banker_name, email, password, branch_code, phone) => {
      setLoading(true);
      try {
        const res = await apiRegister(
          banker_name,
          email,
          password,
          branch_code,
          phone,
        );
        const data = res.data;

        localStorage.setItem("token", data.token);
        localStorage.setItem("banker_id", data.banker_id);
        localStorage.setItem("banker_name", data.banker_name);
        localStorage.setItem("email", data.email);
        localStorage.setItem("branch_code", data.branch_code || "");

        setToken(data.token);
        setUser({
          banker_id: data.banker_id,
          banker_name: data.banker_name,
          email: data.email,
          branch_code: data.branch_code,
        });

        return true;
      } catch (err) {
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const logout = useCallback(async () => {
    try {
      await api.post("/api/v1/auth/logout");
    } catch {
      /* ignore */
    }

    localStorage.removeItem("token");
    localStorage.removeItem("banker_id");
    localStorage.removeItem("banker_name");
    localStorage.removeItem("email");
    localStorage.removeItem("branch_code");

    setToken(null);
    setUser(null);
  }, []);

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export default useAuth;
