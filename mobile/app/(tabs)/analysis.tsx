import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, ScrollView, StyleSheet, RefreshControl, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, FontSize, BorderRadius, Spacing } from '../../constants/theme';
import api, { turkishApiError } from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import SentimentBadge from '../../components/SentimentBadge';

const SECTORS = [
  { id: undefined, label: 'Tüm Sektörler' },
  { id: 1, label: 'SaaS' },
  { id: 2, label: 'Yapay Zeka' },
  { id: 3, label: 'Mobil Uygulamalar' },
];

export default function AnalysisScreen() {
  const [selectedSector, setSelectedSector] = useState<number | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [topics, setTopics] = useState<any[]>([]);
  const [painPoints, setPainPoints] = useState<any[]>([]);
  const [features, setFeatures] = useState<any[]>([]);
  const [sentiments, setSentiments] = useState<any[]>([]);
  const [ratings, setRatings] = useState<any[]>([]);

  const fetchData = useCallback(async (sectorId?: number) => {
    try {
      setError(null);
      const [topicRows, painRows, featureRows, sentimentRows, ratingRows] = await Promise.all([
        api.getTopics(sectorId),
        api.getTopPainPoints(sectorId, 8),
        api.getTopFeatureRequests(sectorId, 8),
        api.getSentimentDistribution(sectorId),
        api.getRatingDistribution(sectorId),
      ]);
      setTopics(Array.isArray(topicRows) ? topicRows : []);
      setPainPoints(Array.isArray(painRows) ? painRows : []);
      setFeatures(Array.isArray(featureRows) ? featureRows : []);
      setSentiments(Array.isArray(sentimentRows) ? sentimentRows : []);
      setRatings(Array.isArray(ratingRows) ? ratingRows : []);
    } catch (err) {
      setError(turkishApiError(err));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchData(selectedSector);
  }, [selectedSector, fetchData]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchData(selectedSector);
  };

  if (loading && topics.length === 0 && sentiments.length === 0) {
    return <LoadingSpinner message="Analizler yükleniyor..." />;
  }

  const maxTopic = Math.max(...topics.map((t) => parseInt(t.review_count || '0', 10)), 1);
  const maxRating = Math.max(...ratings.map((r) => parseInt(r.count || '0', 10)), 1);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.primary} />}
      showsVerticalScrollIndicator={false}
    >
      <Text style={styles.pageTitle}>Analizler</Text>
      <Text style={styles.pageSubtitle}>NLP Duygu, Puan ve Problem Yoğunluğu Analizleri</Text>

      {/* Sektör Seçici */}
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

      {error ? <Text style={styles.error}>{error}</Text> : null}

      {/* Sentiment Dağılımı */}
      <Text style={styles.sectionTitle}>Sentiment (Duygu) Dağılımı</Text>
      {sentiments.length === 0 ? (
        <EmptyState message="Bu sektör için henüz sentiment verisi bulunmuyor." />
      ) : (
        <View style={styles.card}>
          {sentiments.map((item) => (
            <View key={item.sentiment} style={styles.simpleRow}>
              <View style={styles.sentimentLabelGroup}>
                <SentimentBadge sentiment={item.sentiment} />
                {item.avg_confidence ? (
                  <Text style={styles.confidenceText}>
                    Güven: %{(parseFloat(item.avg_confidence) * 100).toFixed(1)}
                  </Text>
                ) : null}
              </View>
              <Text style={styles.count}>{parseInt(item.count || '0', 10).toLocaleString('tr-TR')}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Rating Dağılımı */}
      <Text style={styles.sectionTitle}>Rating Dağılımı</Text>
      {ratings.length === 0 ? (
        <EmptyState message="Bu sektör için henüz puan verisi bulunmuyor." />
      ) : (
        <View style={styles.card}>
          {ratings.map((item) => {
            const count = parseInt(item.count || '0', 10);
            return (
              <View key={item.rating} style={styles.ratingRow}>
                <View style={styles.ratingLabelBox}>
                  <Ionicons name="star" size={13} color={Colors.star} />
                  <Text style={styles.ratingLabel}>{item.rating} yıldız</Text>
                </View>
                <View style={styles.track}>
                  <View style={[styles.ratingFill, { width: `${Math.max((count / maxRating) * 100, 4)}%` }]} />
                </View>
                <Text style={styles.count}>{count.toLocaleString('tr-TR')}</Text>
              </View>
            );
          })}
        </View>
      )}

      {/* Öne Çıkan Konular */}
      <Text style={styles.sectionTitle}>Öne Çıkan Konular</Text>
      {topics.length === 0 ? (
        <EmptyState message="Henüz konu verisi bulunmuyor." icon="pricetags-outline" />
      ) : (
        topics.slice(0, 8).map((item) => {
          const count = parseInt(item.review_count || '0', 10);
          const width = Math.max((count / maxTopic) * 100, 6);
          return (
            <View key={item.topic} style={styles.card}>
              <View style={styles.rowBetween}>
                <Text style={styles.topicName}>{item.topic}</Text>
                <Text style={styles.count}>{count.toLocaleString('tr-TR')} yorum</Text>
              </View>
              <View style={styles.track}>
                <View style={[styles.fill, { width: `${width}%` }]} />
              </View>
              <View style={styles.metaRow}>
                <SentimentBadge sentiment="positive" size="sm" />
                <Text style={styles.meta}>{item.positive_count || 0}</Text>
                <SentimentBadge sentiment="negative" size="sm" />
                <Text style={styles.meta}>{item.negative_count || 0}</Text>
                <Ionicons name="star" size={12} color={Colors.star} />
                <Text style={styles.meta}>{item.average_rating ? Number(item.average_rating).toFixed(1) : '-'}</Text>
              </View>
            </View>
          );
        })
      )}

      {/* Pain Points */}
      <Text style={styles.sectionTitle}>Kullanıcı Şikayetleri (Pain Points)</Text>
      {painPoints.length === 0 ? (
        <EmptyState message="Henüz tespit edilen kritik şikayet bulunmuyor." icon="warning-outline" />
      ) : (
        painPoints.map((item, idx) => (
          <View key={item.pain_point || idx} style={styles.listRow}>
            <View style={styles.iconCircleWarning}>
              <Ionicons name="warning" size={14} color={Colors.negative} />
            </View>
            <Text style={styles.listText}>{item.pain_point}</Text>
            <Text style={styles.countBadge}>{item.count} bildirim</Text>
          </View>
        ))
      )}

      {/* Feature Requests */}
      <Text style={styles.sectionTitle}>Özellik Talepleri (Feature Requests)</Text>
      {features.length === 0 ? (
        <EmptyState message="Henüz özellik talebi bulunmuyor." icon="bulb-outline" />
      ) : (
        features.map((item, idx) => (
          <View key={item.feature_request || idx} style={styles.listRow}>
            <View style={styles.iconCircleFeature}>
              <Ionicons name="bulb" size={14} color={Colors.accent} />
            </View>
            <Text style={styles.listText}>{item.feature_request}</Text>
            <Text style={styles.countBadge}>{item.count} talep</Text>
          </View>
        ))
      )}

      <View style={{ height: 32 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { padding: Spacing.lg },
  pageTitle: { fontSize: FontSize.xxxl, fontWeight: '800', color: Colors.textPrimary },
  pageSubtitle: { fontSize: FontSize.md, color: Colors.textSecondary, marginBottom: Spacing.md },
  filterRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
    paddingBottom: Spacing.md,
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
  sectionTitle: {
    fontSize: FontSize.xl,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginTop: Spacing.xl,
    marginBottom: Spacing.md,
  },
  card: {
    backgroundColor: Colors.backgroundCard,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.md,
  },
  rowBetween: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  topicName: { color: Colors.textPrimary, fontWeight: '700', flex: 1, marginRight: Spacing.md },
  count: { color: Colors.textSecondary, fontWeight: '600' },
  track: {
    height: 8,
    backgroundColor: Colors.surface,
    borderRadius: 4,
    overflow: 'hidden',
    marginTop: Spacing.sm,
    flex: 1,
  },
  fill: { height: '100%', backgroundColor: Colors.primary, borderRadius: 4 },
  ratingFill: { height: '100%', backgroundColor: Colors.star, borderRadius: 4 },
  metaRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: Spacing.sm, flexWrap: 'wrap' },
  meta: { color: Colors.textMuted, fontSize: FontSize.sm },
  simpleRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: Spacing.md },
  sentimentLabelGroup: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
  confidenceText: { color: Colors.textMuted, fontSize: FontSize.xs },
  ratingRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md, marginBottom: Spacing.md },
  ratingLabelBox: { flexDirection: 'row', alignItems: 'center', gap: 4, width: 80 },
  ratingLabel: { color: Colors.textSecondary, fontSize: FontSize.sm },
  listRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: Colors.backgroundCard,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    marginBottom: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: Spacing.md,
  },
  iconCircleWarning: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: 'rgba(255, 82, 82, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconCircleFeature: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: 'rgba(0, 188, 212, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  listText: { color: Colors.textPrimary, flex: 1, fontSize: FontSize.sm },
  countBadge: {
    color: Colors.textMuted,
    fontSize: FontSize.xs,
    fontWeight: '600',
  },
  error: { color: Colors.negative, marginBottom: Spacing.md },
});
