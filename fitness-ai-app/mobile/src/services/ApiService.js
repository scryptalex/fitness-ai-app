import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api' 
  : 'https://your-production-api.com/api';

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Token ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          await AsyncStorage.removeItem('auth_token');
          // Navigate to login screen
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials) {
    const response = await this.api.post('/auth/login/', credentials);
    if (response.data.token) {
      await AsyncStorage.setItem('auth_token', response.data.token);
    }
    return response;
  }

  async register(userData) {
    return await this.api.post('/auth/register/', userData);
  }

  async logout() {
    await AsyncStorage.removeItem('auth_token');
    return await this.api.post('/auth/logout/');
  }

  // User Profile
  async getProfile() {
    return await this.api.get('/users/profile/');
  }

  async updateProfile(profileData) {
    return await this.api.patch('/users/profile/', profileData);
  }

  // Workouts
  async getTodayWorkout() {
    return await this.api.get('/workouts/today/');
  }

  async generateWorkout(preferences = {}) {
    return await this.api.post('/workouts/generate/', preferences);
  }

  async getWorkoutHistory() {
    return await this.api.get('/workouts/history/');
  }

  async startWorkout(workoutId) {
    return await this.api.post(`/workouts/${workoutId}/start/`);
  }

  async completeWorkout(workoutId, completionData) {
    return await this.api.post(`/workouts/${workoutId}/complete/`, completionData);
  }

  // Statistics
  async getWeeklyStats() {
    return await this.api.get('/users/stats/weekly/');
  }

  async getMonthlyStats() {
    return await this.api.get('/users/stats/monthly/');
  }

  // Avatars
  async getAvatars() {
    return await this.api.get('/avatars/');
  }

  async getCurrentAvatar() {
    return await this.api.get('/avatars/current/');
  }

  async updateAvatar(avatarData) {
    return await this.api.patch('/avatars/current/', avatarData);
  }

  // AI Content
  async generateNutritionPlan(preferences) {
    return await this.api.post('/ai/nutrition/', preferences);
  }

  async analyzeHealthData(healthData) {
    return await this.api.post('/ai/health-analysis/', healthData);
  }

  // Medical Data
  async submitHealthData(healthData) {
    return await this.api.post('/medical/health-data/', healthData);
  }

  async getHealthHistory() {
    return await this.api.get('/medical/health-history/');
  }

  // Utility methods
  async uploadImage(imageUri, type = 'profile') {
    const formData = new FormData();
    formData.append('image', {
      uri: imageUri,
      type: 'image/jpeg',
      name: `${type}_image.jpg`,
    });

    return await this.api.post('/upload/image/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  // Check if user is authenticated
  async isAuthenticated() {
    const token = await AsyncStorage.getItem('auth_token');
    return !!token;
  }

  // Get auth token
  async getAuthToken() {
    return await AsyncStorage.getItem('auth_token');
  }
}

export default new ApiService();