import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { Colors, FontSize, BorderRadius, Spacing } from '../../constants/theme';
import api, { turkishApiError } from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import SentimentBadge from '../../components/SentimentBadge';
import RatingStars from '../../components/RatingStars';

export default function ReviewDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const reviewId = parseInt(String(id), 10);
  const [review, setReview] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setError(null);
        setReview(await api.getReview(reviewId));
      } catch (err) {
        setError(turkishApiError(err));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [reviewId]);

  if (loading) return <LoadingSpinner message="Yorum yükleniyor..." />;
  if (error || !review) {
    return (
      <View style={styles.centered}>
        <EmptyState message={error || 'Yorum bulunamadı.'} />
      </View>
    );
  }

  const topics = Array.isArray(review.topics)
    ? review.topics
    : review.topic
      ? [review.topic]
      : [];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <RatingStars rating={Number(review.rating) || 0} />
        <SentimentBadge sentiment={review.sentiment} />
      </View>
      <Text style={styles.meta}>{review.dataset_name} · {review.product_area || 'Ürün belirtilmemiş'}</Text>
      {review.review_date ? (
        <Text style={styles.meta}>
          {new Date(review.review_date).toLocaleDateString('tr-TR')}
        </Text>
      ) : null}

      <Text style={styles.body}>{review.review_text || 'Yorum metni yok.'}</Text>

      <View style={styles.card}>
        <Row label="Sentiment skoru" value={review.sentiment_score ?? '-'} />
        <Row label="Güven skoru" value={review.confidence_score ?? '-'} />
        <Row label="Pain point" value={review.pain_point || 'Yok'} />
        <Row label="Feature request" value={review.feature_request || 'Yok'} />
      </View>

      <Text style={styles.section}>Konular</Text>
      {topics.length === 0 ? (
        <EmptyState message="Bu yoruma ait konu bulunmuyor." />
      ) : (
        topics.map((topic: string) => (
          <View key={topic} style={styles.chip}>
            <Text style={styles.chipText}>{topic}</Text>
          </View>
        ))
      )}
    </ScrollView>
  );
}

function Row({ label, value }: { label: string; value: string | number }) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{String(value)}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { padding: Spacing.lg },
  centered: { flex: 1, backgroundColor: Colors.background, justifyContent: 'center' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: Spacing.md },
  meta: { color: Colors.textMuted, marginBottom: 4 },
  body: { color: Colors.textPrimary, fontSize: FontSize.lg, lineHeight: 24, marginVertical: Spacing.lg },
  card: {
    backgroundColor: Colors.backgroundCard,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  row: { marginBottom: Spacing.md },
  label: { color: Colors.textMuted, fontSize: FontSize.sm },
  value: { color: Colors.textPrimary, marginTop: 2 },
  section: { color: Colors.textPrimary, fontWeight: '700', fontSize: FontSize.xl, marginTop: Spacing.xl, marginBottom: Spacing.md },
  chip: {
    alignSelf: 'flex-start',
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.full,
    paddingHorizontal: Spacing.md,
    paddingVertical: 6,
    marginBottom: Spacing.sm,
  },
  chipText: { color: Colors.primaryLight, fontWeight: '600' },
});
