import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet, RefreshControl } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, BorderRadius, Spacing } from '../../constants/theme';
import api, { turkishApiError } from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import ReviewCard from '../../components/ReviewCard';
import SentimentBadge from '../../components/SentimentBadge';

export default function DatasetDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const datasetId = parseInt(String(id), 10);
  const [dataset, setDataset] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      setError(null);
      const [detail, datasetStats, reviewPage] = await Promise.all([
        api.getDataset(datasetId),
        api.getDatasetStats(datasetId),
        api.getReviews({ dataset_id: datasetId, limit: 8, offset: 0 }),
      ]);
      setDataset(detail);
      setStats(datasetStats);
      setReviews(reviewPage.data);
    } catch (err) {
      setError(turkishApiError(err));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [datasetId]);

  if (loading) return <LoadingSpinner message="Dataset yükleniyor..." />;

  if (error && !dataset) {
    return (
      <View style={styles.centered}>
        <EmptyState message={error} icon="cloud-offline-outline" />
      </View>
    );
  }

  const overview = stats?.overview || {};
  const sentiments = stats?.sentiment_distribution || [];

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchData(); }} tintColor={Colors.primary} />}
    >
      <Text style={styles.title}>{dataset?.name}</Text>
      <Text style={styles.sub}>{dataset?.subsector} · {dataset?.data_period}</Text>
      {dataset?.description ? <Text style={styles.desc}>{dataset.description}</Text> : null}

      <View style={styles.statsRow}>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{parseInt(overview.total_reviews || dataset?.actual_review_count || '0').toLocaleString('tr-TR')}</Text>
          <Text style={styles.statLabel}>Yorum</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{overview.avg_rating || '-'}</Text>
          <Text style={styles.statLabel}>Ort. rating</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{parseInt(overview.analyzed_reviews || '0').toLocaleString('tr-TR')}</Text>
          <Text style={styles.statLabel}>Analiz</Text>
        </View>
      </View>

      <Text style={styles.section}>Kaynak</Text>
      <Text style={styles.meta}>{dataset?.source || 'Belirtilmemiş'} · {dataset?.license || 'N/A'}</Text>

      <Text style={styles.section}>Sentiment</Text>
      {sentiments.length === 0 ? (
        <EmptyState message="Bu dataset için sentiment verisi yok." />
      ) : (
        sentiments.map((item: any) => (
          <View key={item.sentiment} style={styles.row}>
            <SentimentBadge sentiment={item.sentiment} />
            <Text style={styles.count}>{parseInt(item.count || '0').toLocaleString('tr-TR')}</Text>
          </View>
        ))
      )}

      <Text style={styles.section}>Örnek yorumlar</Text>
      {reviews.length === 0 ? (
        <EmptyState message="Bu dataset için yorum bulunmuyor." />
      ) : (
        reviews.map((review) => (
          <ReviewCard
            key={review.id}
            review={review}
            compact
            onPress={() => router.push(`/review/${review.id}`)}
          />
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { padding: Spacing.lg },
  centered: { flex: 1, backgroundColor: Colors.background, justifyContent: 'center' },
  title: { fontSize: FontSize.xxl, fontWeight: '800', color: Colors.textPrimary },
  sub: { color: Colors.primaryLight, marginTop: 4, marginBottom: Spacing.md },
  desc: { color: Colors.textSecondary, lineHeight: 20, marginBottom: Spacing.lg },
  statsRow: { flexDirection: 'row', gap: Spacing.md, marginBottom: Spacing.lg },
  statBox: {
    flex: 1,
    backgroundColor: Colors.backgroundCard,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
    alignItems: 'center',
  },
  statValue: { color: Colors.textPrimary, fontWeight: '700', fontSize: FontSize.lg },
  statLabel: { color: Colors.textMuted, fontSize: FontSize.xs, marginTop: 4 },
  section: { color: Colors.textPrimary, fontWeight: '700', fontSize: FontSize.xl, marginTop: Spacing.lg, marginBottom: Spacing.md },
  meta: { color: Colors.textSecondary },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: Spacing.sm },
  count: { color: Colors.textSecondary, fontWeight: '600' },
});
