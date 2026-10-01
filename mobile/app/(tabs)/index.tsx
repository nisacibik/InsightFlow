import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet, RefreshControl, Dimensions } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, BorderRadius, Spacing } from '../../constants/theme';
import api, { turkishApiError } from '../../services/api';
import StatCard from '../../components/StatCard';
import ReviewCard from '../../components/ReviewCard';
import SentimentBadge from '../../components/SentimentBadge';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

export default function DashboardScreen() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setError(null);
      const result = await api.getDashboard();
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Veriler yüklenemedi. Lütfen tekrar deneyin.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  if (loading) return <LoadingSpinner message="Dashboard yükleniyor..." />;

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="cloud-offline-outline" size={64} color={Colors.negative} />
        <Text style={styles.errorTitle}>Bağlantı Hatası</Text>
        <Text style={styles.errorText}>{error}</Text>
        <Text style={styles.errorHint}>Backend sunucusunun çalıştığından emin olun{'\n'}(node server.js)</Text>
      </View>
    );
  }

  const overview = data?.overview;
  const sentiments = data?.sentiment_distribution || [];
  const ratings = data?.rating_distribution || [];
  const recentReviews = data?.recent_reviews || [];
  const products = data?.product_distribution || [];

  const totalSentiment = sentiments.reduce((sum: number, s: any) => sum + parseInt(s.count), 0);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.primary} />}
      showsVerticalScrollIndicator={false}
    >
      {/* Hero Header */}
      <View style={styles.heroSection}>
        <Text style={styles.heroTitle}>InsightFlow</Text>
        <Text style={styles.heroSubtitle}>Review Analytics Dashboard</Text>
      </View>

      {/* Stat Cards */}
      <View style={styles.statsRow}>
        <StatCard
          title="Toplam Yorum"
          value={parseInt(overview?.total_reviews || '0').toLocaleString()}
          icon="chatbubbles"
          color={Colors.primary}
        />
        <StatCard
          title="Ort. Rating"
          value={parseFloat(overview?.avg_rating || '0').toFixed(1)}
          icon="star"
          color={Colors.star}
        />
      </View>
      <View style={styles.statsRow}>
        <StatCard
          title="Datasets"
          value={overview?.total_datasets || '0'}
          icon="layers"
          color={Colors.accent}
        />
        <StatCard
          title="Analizler"
          value={parseInt(overview?.total_analyses || '0').toLocaleString()}
          icon="analytics"
          color={Colors.info}
        />
      </View>

      {/* Sentiment Distribution */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Sentiment Dağılımı</Text>
        <View style={styles.sentimentCard}>
          {/* Bar chart */}
          <View style={styles.barContainer}>
            {sentiments.map((item: any) => {
              const percentage = totalSentiment > 0 ? (parseInt(item.count) / totalSentiment) * 100 : 0;
              const barColor =
                item.sentiment === 'positive' ? Colors.positive :
                item.sentiment === 'negative' ? Colors.negative : Colors.neutral;
              return (
                <View key={item.sentiment} style={styles.barItem}>
                  <Text style={styles.barPercentage}>{percentage.toFixed(1)}%</Text>
                  <View style={styles.barTrack}>
                    <View style={[styles.barFill, { height: `${Math.max(percentage, 3)}%`, backgroundColor: barColor }]} />
                  </View>
                  <SentimentBadge sentiment={item.sentiment} size="sm" />
                  <Text style={styles.barCount}>{parseInt(item.count).toLocaleString()}</Text>
                </View>
              );
            })}
          </View>
        </View>
      </View>

      {/* Rating Distribution */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Rating Dağılımı</Text>
        <View style={styles.ratingCard}>
          {ratings.map((item: any) => {
            const maxCount = Math.max(...ratings.map((r: any) => parseInt(r.count)));
            const barWidth = maxCount > 0 ? (parseInt(item.count) / maxCount) * 100 : 0;
            return (
              <View key={item.rating} style={styles.ratingRow}>
                <View style={styles.ratingLabel}>
                  <Ionicons name="star" size={14} color={Colors.star} />
                  <Text style={styles.ratingText}>{item.rating}</Text>
                </View>
                <View style={styles.ratingBarTrack}>
                  <View style={[styles.ratingBarFill, { width: `${barWidth}%` }]} />
                </View>
                <Text style={styles.ratingCount}>{parseInt(item.count).toLocaleString()}</Text>
              </View>
            );
          })}
        </View>
      </View>

      {/* Product Distribution */}
      {products.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Ürün Alanları</Text>
          <View style={styles.productCard}>
            {products.map((item: any, index: number) => {
              const colors = [Colors.primary, Colors.accent, Colors.info, Colors.positive, Colors.neutral];
              return (
                <View key={item.product_area} style={styles.productRow}>
                  <View style={[styles.productDot, { backgroundColor: colors[index % colors.length] }]} />
                  <Text style={styles.productName} numberOfLines={1}>{item.product_area}</Text>
                  <Text style={styles.productCount}>{parseInt(item.count).toLocaleString()}</Text>
                </View>
              );
            })}
          </View>
        </View>
      )}

      {Array.isArray(data?.top_topics) && data.top_topics.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Öne Çıkan Konular</Text>
          <View style={styles.productCard}>
            {data.top_topics.slice(0, 6).map((item: any) => (
              <View key={item.topic} style={styles.productRow}>
                <View style={[styles.productDot, { backgroundColor: Colors.primary }]} />
                <Text style={styles.productName} numberOfLines={1}>{item.topic}</Text>
                <Text style={styles.productCount}>{parseInt(item.review_count || '0').toLocaleString()}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Recent Reviews */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Son Yorumlar</Text>
        {recentReviews.slice(0, 5).map((review: any) => (
          <ReviewCard
            key={review.id}
            review={review}
            compact
            onPress={() => router.push(`/review/${review.id}`)}
          />
        ))}
      </View>

      <View style={{ height: 30 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    padding: Spacing.lg,
  },
  heroSection: {
    paddingVertical: Spacing.xl,
    paddingHorizontal: Spacing.sm,
    marginBottom: Spacing.lg,
  },
  heroTitle: {
    fontSize: FontSize.hero,
    fontWeight: '800',
    color: Colors.textPrimary,
    letterSpacing: -0.5,
  },
  heroSubtitle: {
    fontSize: FontSize.lg,
    color: Colors.primaryLight,
    marginTop: 4,
    fontWeight: '500',
  },
  statsRow: {
    flexDirection: 'row',
    gap: Spacing.md,
    marginBottom: Spacing.md,
  },
  section: {
    marginTop: Spacing.xl,
  },
  sectionTitle: {
    fontSize: FontSize.xl,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginBottom: Spacing.lg,
  },
  sentimentCard: {
    backgroundColor: Colors.backgroundCard,
    borderRadius: BorderRadius.lg,
    padding: Spacing.xl,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  barContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'flex-end',
    height: 180,
  },
  barItem: {
    alignItems: 'center',
    flex: 1,
  },
  barPercentage: {
    fontSize: FontSize.sm,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginBottom: Spacing.sm,
  },
  barTrack: {
    width: 40,
    height: 100,
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.sm,
    overflow: 'hidden',
    justifyContent: 'flex-end',
    marginBottom: Spacing.sm,
  },
  barFill: {
    width: '100%',
    borderRadius: BorderRadius.sm,
  },
  barCount: {
    fontSize: FontSize.xs,
    color: Colors.textMuted,
    marginTop: 4,
  },
  ratingCard: {
    backgroundColor: Colors.backgroundCard,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  ratingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  ratingLabel: {
    flexDirection: 'row',
    alignItems: 'center',
    width: 36,
    gap: 4,
  },
  ratingText: {
    fontSize: FontSize.sm,
    color: Colors.textSecondary,
    fontWeight: '600',
  },
  ratingBarTrack: {
    flex: 1,
    height: 8,
    backgroundColor: Colors.surface,
    borderRadius: 4,
    marginHorizontal: Spacing.md,
    overflow: 'hidden',
  },
  ratingBarFill: {
    height: '100%',
    backgroundColor: Colors.star,
    borderRadius: 4,
  },
  ratingCount: {
    fontSize: FontSize.sm,
    color: Colors.textSecondary,
    width: 60,
    textAlign: 'right',
    fontWeight: '600',
  },
  productCard: {
    backgroundColor: Colors.backgroundCard,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  productRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.sm,
  },
  productDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: Spacing.md,
  },
  productName: {
    flex: 1,
    fontSize: FontSize.md,
    color: Colors.textPrimary,
  },
  productCount: {
    fontSize: FontSize.md,
    color: Colors.textSecondary,
    fontWeight: '600',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.background,
    padding: Spacing.xxxl,
  },
  errorTitle: {
    fontSize: FontSize.xxl,
    fontWeight: '700',
    color: Colors.negative,
    marginTop: Spacing.lg,
  },
  errorText: {
    fontSize: FontSize.md,
    color: Colors.textSecondary,
    marginTop: Spacing.sm,
    textAlign: 'center',
  },
  errorHint: {
    fontSize: FontSize.sm,
    color: Colors.textMuted,
    marginTop: Spacing.lg,
    textAlign: 'center',
    lineHeight: 20,
  },
});
