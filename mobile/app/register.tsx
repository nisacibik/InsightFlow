import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { Redirect, useRouter } from 'expo-router';
import { Colors, FontSize, BorderRadius, Spacing } from '../constants/theme';
import { useAuth } from '../contexts/AuthContext';

export default function RegisterScreen() {
  const router = useRouter();
  const { user, register, loading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  if (user) return <Redirect href="/(tabs)" />;

  const validate = (): boolean => {
    setLocalError(null);

    if (!email.trim()) {
      setLocalError('E-posta adresi boş bırakılamaz.');
      return false;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setLocalError('Geçerli bir e-posta adresi girin.');
      return false;
    }
    if (!password) {
      setLocalError('Şifre boş bırakılamaz.');
      return false;
    }
    if (password.length < 6) {
      setLocalError('Şifre en az 6 karakter olmalı.');
      return false;
    }
    if (password !== passwordConfirm) {
      setLocalError('Şifreler eşleşmiyor.');
      return false;
    }
    return true;
  };

  const onSubmit = async () => {
    if (!validate()) return;
    const ok = await register(email, password);
    if (ok) router.replace('/company-setup');
  };

  const displayError = localError || error;

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>Hesap Oluştur</Text>
        <Text style={styles.subtitle}>E-posta ve şifre ile kayıt olun</Text>

        <TextInput
          style={styles.input}
          placeholder="E-posta"
          placeholderTextColor={Colors.textMuted}
          autoCapitalize="none"
          keyboardType="email-address"
          value={email}
          onChangeText={(t) => { setEmail(t); setLocalError(null); }}
        />
        <TextInput
          style={styles.input}
          placeholder="Şifre (en az 6 karakter)"
          placeholderTextColor={Colors.textMuted}
          secureTextEntry
          value={password}
          onChangeText={(t) => { setPassword(t); setLocalError(null); }}
        />
        <TextInput
          style={styles.input}
          placeholder="Şifre tekrar"
          placeholderTextColor={Colors.textMuted}
          secureTextEntry
          value={passwordConfirm}
          onChangeText={(t) => { setPasswordConfirm(t); setLocalError(null); }}
        />

        {displayError ? <Text style={styles.error}>{displayError}</Text> : null}

        <TouchableOpacity style={styles.button} onPress={onSubmit} disabled={loading}>
          <Text style={styles.buttonText}>{loading ? 'Kaydediliyor...' : 'Kayıt Ol'}</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: Colors.background },
  content: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: Spacing.xxl,
  },
  title: {
    fontSize: FontSize.xxxl,
    fontWeight: '800',
    color: Colors.textPrimary,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: FontSize.md,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginBottom: Spacing.xxxl,
    marginTop: Spacing.sm,
  },
  input: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    color: Colors.textPrimary,
    paddingHorizontal: Spacing.lg,
    paddingVertical: 14,
    marginBottom: Spacing.md,
    fontSize: FontSize.lg,
  },
  button: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.md,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: Spacing.sm,
  },
  buttonText: {
    color: Colors.white,
    fontWeight: '700',
    fontSize: FontSize.lg,
  },
  error: {
    color: Colors.negative,
    textAlign: 'center',
    marginBottom: Spacing.md,
  },
});
