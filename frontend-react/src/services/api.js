import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// Auto-attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 → logout
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      // Redirect will be handled by auth state or manual reload if needed
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export const login = async (email, password) => {
  return api.post("/api/v1/auth/login", { email, password });
};

export const register = async (banker_name, email, password, branch_code, phone) => {
  return api.post("/api/v1/auth/register", {
    banker_name,
    email,
    password,
    branch_code: branch_code || null,
    phone: phone || null,
  });
};

export const verifyIdentity = async (liveBlob, refBlob, userId) => {
  const formData = new FormData();
  formData.append("live_image", liveBlob, "live.jpg");
  formData.append("reference_image", refBlob, "ref.jpg");
  if (userId) formData.append("user_id", userId);

  return api.post("/api/v1/verify", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const submitDecision = async (decisionId, action, reasoning) => {
  return api.post("/api/v1/decide", {
    decision_id: decisionId,
    action,
    reasoning,
  });
};

export default api;
