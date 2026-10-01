import React from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { Colors, FontSize } from '../constants/theme';

interface LoadingSpinnerProps {
  message?: string;
}

export default function LoadingSpinner({ message = 'Yükleniyor...' }: LoadingSpinnerProps) {
  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color={Colors.primary} />
      <Text style={styles.message}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.background,
    padding: 20,
  },
  message: {
    marginTop: 16,
    fontSize: FontSize.md,
    color: Colors.textSecondary,
  },
});
