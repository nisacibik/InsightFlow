import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, BorderRadius, Spacing } from '../constants/theme';
import SentimentBadge from './SentimentBadge';
import RatingStars from './RatingStars';

interface ReviewCardProps {
  review: {
    id: string;
    review_text: string;
    rating: number;
    product_area?: string;
    review_date?: string;
    sentiment?: string;
    sentiment_score?: string;
    dataset_name?: string;
    helpful_count?: number;
  };
  onPress?: () => void;
  compact?: boolean;
}

export default function ReviewCard({ review, onPress, compact = false }: ReviewCardProps) {
  const text = review.review_text || '';
  const truncatedText = compact
    ? text.substring(0, 120) + (text.length > 120 ? '...' : '')
    : text.substring(0, 200) + (text.length > 200 ? '...' : '');

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('tr-TR', { day: '2-digit', month: 'short', year: 'numeric' });
  };

  return (
    <TouchableOpacity
      style={[styles.card, compact && styles.cardCompact]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.header}>
        <View style={styles.ratingRow}>
          <RatingStars rating={review.rating} size={14} />
          <SentimentBadge sentiment={review.sentiment || null} size="sm" />
        </View>
      </View>

      <Text style={styles.reviewText}>{truncatedText}</Text>

      <View style={styles.footer}>
        <View style={styles.metaRow}>
          {review.dataset_name && (
            <View style={styles.metaItem}>
              <Ionicons name="folder-outline" size={12} color={Colors.textMuted} />
              <Text style={styles.metaText} numberOfLines={1}>
                {review.dataset_name.length > 20 ? review.dataset_name.substring(0, 20) + '...' : review.dataset_name}
              </Text>
            </View>
          )}
          {review.review_date && (
            <View style={styles.metaItem}>
              <Ionicons name="calendar-outline" size={12} color={Colors.textMuted} />
              <Text style={styles.metaText}>{formatDate(review.review_date)}</Text>
            </View>
          )}
        </View>
        {review.sentiment_score && (
          <Text style={styles.scoreText}>
            Score: {parseFloat(review.sentiment_score).toFixed(2)}
          </Text>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.backgroundCard,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.md,
  },
  cardCompact: {
    padding: Spacing.md,
  },
  header: {
    marginBottom: Spacing.sm,
  },
  ratingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  reviewText: {
    fontSize: FontSize.md,
    color: Colors.textPrimary,
    lineHeight: 20,
    marginBottom: Spacing.md,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
    flex: 1,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  metaText: {
    fontSize: FontSize.xs,
    color: Colors.textMuted,
  },
  scoreText: {
    fontSize: FontSize.xs,
    color: Colors.primaryLight,
    fontWeight: '600',
  },
});
