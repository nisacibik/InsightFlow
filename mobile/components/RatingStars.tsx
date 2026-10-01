import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../constants/theme';

interface RatingStarsProps {
  rating: number;
  size?: number;
  color?: string;
}

export default function RatingStars({ rating, size = 16, color = Colors.star }: RatingStarsProps) {
  return (
    <View style={styles.container}>
      {[1, 2, 3, 4, 5].map((star) => (
        <Ionicons
          key={star}
          name={star <= rating ? 'star' : star - rating < 1 ? 'star-half' : 'star-outline'}
          size={size}
          color={star <= rating ? color : Colors.starEmpty}
          style={{ marginRight: 1 }}
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
  },
});
