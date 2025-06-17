import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import {Card, Button} from 'react-native-elements';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialIcons';
import ApiService from '../services/ApiService';

const HomeScreen = ({navigation}) => {
  const [todayWorkout, setTodayWorkout] = useState(null);
  const [stats, setStats] = useState({
    workoutsThisWeek: 0,
    caloriesBurned: 0,
    streakDays: 0,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadHomeData();
  }, []);

  const loadHomeData = async () => {
    try {
      setLoading(true);
      const [workoutResponse, statsResponse] = await Promise.all([
        ApiService.getTodayWorkout(),
        ApiService.getWeeklyStats(),
      ]);
      
      setTodayWorkout(workoutResponse.data);
      setStats(statsResponse.data);
    } catch (error) {
      console.error('Error loading home data:', error);
      Alert.alert('Error', 'Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const generateNewWorkout = async () => {
    try {
      setLoading(true);
      const response = await ApiService.generateWorkout();
      setTodayWorkout(response.data);
      Alert.alert('Success', 'New workout generated!');
    } catch (error) {
      console.error('Error generating workout:', error);
      Alert.alert('Error', 'Failed to generate workout. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: 'Start Workout',
      icon: 'play-arrow',
      color: '#4CAF50',
      onPress: () => navigation.navigate('Workout'),
    },
    {
      title: 'View Avatar',
      icon: 'person',
      color: '#2196F3',
      onPress: () => navigation.navigate('Avatar'),
    },
    {
      title: 'Track Progress',
      icon: 'trending-up',
      color: '#FF9800',
      onPress: () => navigation.navigate('Profile'),
    },
    {
      title: 'New Workout',
      icon: 'refresh',
      color: '#9C27B0',
      onPress: generateNewWorkout,
    },
  ];

  return (
    <LinearGradient colors={['#FF6B6B', '#4ECDC4']} style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.greeting}>Good Morning!</Text>
          <Text style={styles.subtitle}>Ready for today's workout?</Text>
        </View>

        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <Card containerStyle={styles.statCard}>
            <Text style={styles.statNumber}>{stats.workoutsThisWeek}</Text>
            <Text style={styles.statLabel}>Workouts This Week</Text>
          </Card>
          <Card containerStyle={styles.statCard}>
            <Text style={styles.statNumber}>{stats.caloriesBurned}</Text>
            <Text style={styles.statLabel}>Calories Burned</Text>
          </Card>
          <Card containerStyle={styles.statCard}>
            <Text style={styles.statNumber}>{stats.streakDays}</Text>
            <Text style={styles.statLabel}>Day Streak</Text>
          </Card>
        </View>

        {/* Today's Workout */}
        <Card containerStyle={styles.workoutCard}>
          <Text style={styles.cardTitle}>Today's Workout</Text>
          {todayWorkout ? (
            <View>
              <Text style={styles.workoutTitle}>{todayWorkout.title}</Text>
              <Text style={styles.workoutDescription}>
                {todayWorkout.description}
              </Text>
              <Text style={styles.workoutDuration}>
                Duration: {todayWorkout.duration} minutes
              </Text>
            </View>
          ) : (
            <Text style={styles.noWorkoutText}>
              No workout planned for today. Generate one now!
            </Text>
          )}
          <Button
            title={todayWorkout ? 'Start Workout' : 'Generate Workout'}
            buttonStyle={styles.workoutButton}
            onPress={
              todayWorkout
                ? () => navigation.navigate('Workout')
                : generateNewWorkout
            }
            loading={loading}
          />
        </Card>

        {/* Quick Actions */}
        <View style={styles.quickActionsContainer}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionsGrid}>
            {quickActions.map((action, index) => (
              <TouchableOpacity
                key={index}
                style={[styles.actionButton, {backgroundColor: action.color}]}
                onPress={action.onPress}>
                <Icon name={action.icon} size={30} color="white" />
                <Text style={styles.actionText}>{action.title}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </ScrollView>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
    padding: 20,
  },
  header: {
    marginBottom: 20,
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    marginHorizontal: 5,
    borderRadius: 10,
    alignItems: 'center',
    paddingVertical: 15,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FF6B6B',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  workoutCard: {
    borderRadius: 15,
    marginBottom: 20,
    padding: 20,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  workoutTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 10,
    color: '#FF6B6B',
  },
  workoutDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  workoutDuration: {
    fontSize: 14,
    fontWeight: '500',
    color: '#4ECDC4',
    marginBottom: 15,
  },
  noWorkoutText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 15,
  },
  workoutButton: {
    backgroundColor: '#FF6B6B',
    borderRadius: 25,
    paddingVertical: 12,
  },
  quickActionsContainer: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 15,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    width: '48%',
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
    marginBottom: 10,
  },
  actionText: {
    color: 'white',
    fontWeight: '600',
    marginTop: 5,
    textAlign: 'center',
  },
});

export default HomeScreen;