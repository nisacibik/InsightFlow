import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  Dimensions,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, BorderRadius, Spacing } from '../../constants/theme';
import api, { turkishApiError } from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import SentimentBadge from '../../components/SentimentBadge';

interface TopicItem {
  topic: string;
  review_count: number | string;
  positive_count: number | string;
  negative_count: number | string;
  neutral_count: number | string;
  average_rating: number | string;
  product_area?: string;
}

const SECTORS = [
  { id: undefined, label: 'Tüm Sektörler' },
  { id: 1, label: 'SaaS' },
  { id: 2, label: 'Yapay Zeka' },
  { id: 3, label: 'Mobil Uygulamalar' },
];

export default function TopicsScreen() {
  const router = useRouter();
  const [selectedSector, setSelectedSector] = useState<number | undefined>(undefined);
  const [topics, setTopics] = useState<TopicItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTopicsData = useCallback(async (sectorId?: number) => {
    try {
      setError(null);
      const rows = await api.getTopics(sectorId);
      setTopics(Array.isArray(rows) ? rows : []);
    } catch (err) {
      setError(turkishApiError(err, 'Konular yüklenemedi. Lütfen tekrar deneyin.'));
      setTopics([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchTopicsData(selectedSector);
  }, [selectedSector, fetchTopicsData]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchTopicsData(selectedSector);
  };

  if (loading && topics.length === 0) {
    return <LoadingSpinner message="Konular analiz ediliyor..." />;
  }

  const maxCount = Math.max(...topics.map((t) => parseInt(String(t.review_count || '0'), 10)), 1);
  const totalCount = topics.reduce((sum, t) => sum + parseInt(String(t.review_count || '0'), 10), 0);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.primary} />
      }
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.header}>
        <Text style={styles.pageTitle}>Konular</Text>
        <Text style={styles.pageSubtitle}>
          Kullanıcı yorumlarından çıkarılan ana temalar ve NLP duygu analizi
        </Text>
      </View>

      {/* Sektör Filtresi */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.filterRow}
      >
        {SECTORS.map((sec) => {
          const isActive = selectedSector === sec.id;
          return (
            <TouchableOpacity
              key={sec.label}
              style={[styles.chip, isActive && styles.chipActive]}
              onPress={() => setSelectedSector(sec.id)}
              activeOpacity={0.7}
            >
              <Text style={[styles.chipText, isActive && styles.chipTextActive]}>
                {sec.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      {error ? <Text style={styles.errorText}>{error}</Text> : null}

      {/* Özet Barı */}
      <View style={styles.summaryBar}>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryNum}>{topics.length}</Text>
          <Text style={styles.summaryLabel}>Konu</Text>
        </View>
        <View style={styles.summaryDivider} />
        <View style={styles.summaryItem}>
          <Text style={styles.summaryNum}>{totalCount.toLocaleString('tr-TR')}</Text>
          <Text style={styles.summaryLabel}>Etiketlenen Yorum</Text>
        </View>
      </View>

      {/* Konu Kartları */}
      {topics.length === 0 && !loading ? (
        <EmptyState
          message="Bu sektör için henüz konu analizi bulunmuyor."
          icon="pricetags-outline"
        />
      ) : (
        topics.map((item, index) => {
          const count = parseInt(String(item.review_count || '0'), 10);
          const pos = parseInt(String(item.positive_count || '0'), 10);
          const neg = parseInt(String(item.negative_count || '0'), 10);
          const neu = parseInt(String(item.neutral_count || '0'), 10);
          const percentage = Math.max((count / maxCount) * 100, 5);

          return (
            <View key={item.topic || String(index)} style={styles.topicCard}>
              <View style={styles.cardHeader}>
                <View style={styles.topicRankBadge}>
                  <Text style={styles.topicRankText}>#{index + 1}</Text>
                </View>
                <Text style={styles.topicTitle} numberOfLines={1}>
                  {item.topic}
                </Text>
                <Text style={styles.countBadge}>{count.toLocaleString('tr-TR')} yorum</Text>
              </View>

              {/* Progress Bar */}
              <View style={styles.progressTrack}>
                <View style={[styles.progressFill, { width: `${percentage}%` }]} />
              </View>

              {/* Sentiment Dağılımı ve Ortalama Puan */}
              <View style={styles.metaRow}>
                <View style={styles.sentimentItem}>
                  <SentimentBadge sentiment="positive" size="sm" />
                  <Text style={styles.metaText}>{pos.toLocaleString('tr-TR')}</Text>
                </View>
                <View style={styles.sentimentItem}>
                  <SentimentBadge sentiment="negative" size="sm" />
                  <Text style={styles.metaText}>{neg.toLocaleString('tr-TR')}</Text>
                </View>
                {neu > 0 && (
                  <View style={styles.sentimentItem}>
                    <SentimentBadge sentiment="neutral" size="sm" />
                    <Text style={styles.metaText}>{neu.toLocaleString('tr-TR')}</Text>
                  </View>
                )}
                <View style={styles.ratingBadge}>
                  <Ionicons name="star" size={14} color={Colors.star} />
                  <Text style={styles.ratingText}>
                    {item.average_rating ? Number(item.average_rating).toFixed(1) : '-'}
                  </Text>
                </View>
              </View>
            </View>
          );
        })
      )}

      <View style={{ height: 32 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { padding: Spacing.lg },
  header: { marginBottom: Spacing.md },
  pageTitle: {
    fontSize: FontSize.xxxl,
    fontWeight: '800',
    color: Colors.textPrimary,
  },
  pageSubtitle: {
    fontSize: FontSize.md,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  filterRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
    paddingVertical: Spacing.md,
  },
  chip: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: 8,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  chipActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primaryLight,
  },
  chipText: {
    color: Colors.textSecondary,
    fontWeight: '600',
    fontSize: FontSize.sm,
  },
  chipTextActive: {
    color: Colors.white,
    fontWeight: '700',
  },
  summaryBar: {
    flexDirection: 'row',
    backgroundColor: Colors.backgroundCard,
    borderRadius: BorderRadius.lg,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.lg,
  },
  summaryItem: { flex: 1, alignItems: 'center' },
  summaryNum: {
    fontSize: FontSize.xl,
    fontWeight: '800',
    color: Colors.textPrimary,
  },
  summaryLabel: {
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    marginTop: 2,
  },
  summaryDivider: {
    width: 1,
    backgroundColor: Colors.border,
    marginVertical: 4,
  },
  topicCard: {
    backgroundColor: Colors.backgroundCard,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.md,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  topicRankBadge: {
    backgroundColor: 'rgba(108, 92, 231, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: BorderRadius.sm,
    marginRight: Spacing.sm,
  },
  topicRankText: {
    color: Colors.primaryLight,
    fontWeight: '800',
    fontSize: FontSize.xs,
  },
  topicTitle: {
    flex: 1,
    fontSize: FontSize.lg,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  countBadge: {
    color: Colors.primaryLight,
    fontSize: FontSize.xs,
    fontWeight: '700',
  },
  progressTrack: {
    height: 8,
    backgroundColor: Colors.surface,
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: Spacing.md,
  },
  progressFill: {
    height: '100%',
    backgroundColor: Colors.primary,
    borderRadius: 4,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
    flexWrap: 'wrap',
  },
  sentimentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  metaText: {
    color: Colors.textMuted,
    fontSize: FontSize.xs,
    fontWeight: '600',
  },
  ratingBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginLeft: 'auto',
    backgroundColor: Colors.surface,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: BorderRadius.sm,
  },
  ratingText: {
    color: Colors.star,
    fontWeight: '700',
    fontSize: FontSize.sm,
  },
  errorText: {
    color: Colors.negative,
    marginBottom: Spacing.md,
  },
});
