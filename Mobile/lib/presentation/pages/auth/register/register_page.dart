import 'package:flutter/material.dart';
import 'package:iconify_flutter/iconify_flutter.dart';
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_spacing.dart';
import 'package:progressio_mobile/core/constants/app_typography.dart';
import 'package:progressio_mobile/core/constants/cute_iconify_icons.dart';
import 'package:progressio_mobile/presentation/pages/auth/login/widgets/animated_text_field.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// RegisterFormContent — Konten form kartu register (tanpa scaffold/header duplikat)
/// Digunakan untuk transisi in-place fluid di dalam satu kartu.
/// ─────────────────────────────────────────────────────────────────────────────
class RegisterFormContent extends StatefulWidget {
  final VoidCallback onSwitchToLogin;

  const RegisterFormContent({
    super.key,
    required this.onSwitchToLogin,
  });

  @override
  State<RegisterFormContent> createState() => _RegisterFormContentState();
}

class _RegisterFormContentState extends State<RegisterFormContent> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _passwordController.addListener(_onPasswordChanged);
  }

  void _onPasswordChanged() {
    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    _passwordController.removeListener(_onPasswordChanged);
    _fullNameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  int _calculatePasswordStrength(String password) {
    if (password.isEmpty) return 0;
    int score = 0;
    if (password.length >= 6) score++;
    if (password.length >= 8 &&
        RegExp(r'[A-Za-z]').hasMatch(password) &&
        RegExp(r'[0-9]').hasMatch(password)) {
      score++;
    }
    if (password.length >= 10 &&
        RegExp(r'[!@#\$%^&*(),.?":{}|<>]').hasMatch(password)) {
      score++;
    }
    return score.clamp(1, 3);
  }

  String _getStrengthLabel(int strength) {
    switch (strength) {
      case 1:
        return 'Lemah';
      case 2:
        return 'Sedang';
      case 3:
        return 'Kuat';
      default:
        return 'Lemah';
    }
  }

  Color _getStrengthColor(int strength) {
    switch (strength) {
      case 1:
        return AppColors.heartRed;
      case 2:
        return const Color(0xFF8CE323);
      case 3:
        return AppColors.limeDeep;
      default:
        return const Color(0xFFE2E8DE);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Handle Pill Bar
          Center(
            child: Container(
              width: 44,
              height: 4.5,
              decoration: BoxDecoration(
                color: const Color(0xFFE2E8DE),
                borderRadius: BorderRadius.circular(3),
              ),
            ),
          ),
          const SizedBox(height: 14),

          // Headline: "Mulai Petualanganmu! 🚀"
          Wrap(
            alignment: WrapAlignment.center,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: const [
              Text(
                'Mulai Petualanganmu!',
                style: TextStyle(
                  fontFamily: AppTypography.headlineFont,
                  fontSize: 22,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textMain,
                ),
              ),
              SizedBox(width: 8),
              Text(
                '🚀',
                style: TextStyle(fontSize: 21),
              ),
            ],
          ),

          const SizedBox(height: 6),

          // Subtitle
          const Text(
            'Buat akun dan ubah progres belajarmu jadi bukti nyata',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontFamily: AppTypography.bodyFont,
              fontSize: 12.5,
              color: AppColors.textMuted,
              fontWeight: FontWeight.w500,
            ),
          ),

          const SizedBox(height: 16),

          // Field 1: Nama Lengkap
          AnimatedDopamineTextField(
            controller: _fullNameController,
            label: 'Nama Lengkap',
            hintText: 'Masukkan nama lengkap kamu',
            iconifySvg: CuteIconifyIcons.userCute,
            activeColor: AppColors.lavenderPrimary,
            keyboardType: TextInputType.name,
            validator: (value) {
              if (value == null || value.trim().isEmpty) {
                return 'Nama lengkap wajib diisi';
              }
              return null;
            },
          ),

          const SizedBox(height: 12),

          // Field 2: Email Belajar
          AnimatedDopamineTextField(
            controller: _emailController,
            label: 'Email Belajar',
            hintText: 'Masukkan email kamu',
            iconifySvg: CuteIconifyIcons.emailCute,
            activeColor: AppColors.lavenderPrimary,
            keyboardType: TextInputType.emailAddress,
            validator: (value) {
              if (value == null || value.trim().isEmpty) {
                return 'Email wajib diisi';
              }
              if (!value.contains('@')) {
                return 'Format email tidak valid';
              }
              return null;
            },
          ),

          const SizedBox(height: 12),

          // Field 3: Kata Sandi
          AnimatedDopamineTextField(
            controller: _passwordController,
            label: 'Kata Sandi',
            hintText: 'Buat kata sandi aman',
            iconifySvg: CuteIconifyIcons.lockCute,
            activeColor: const Color(0xFF8CE323),
            isPassword: true,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Kata sandi wajib diisi';
              }
              if (value.length < 6) {
                return 'Kata sandi minimal 6 karakter';
              }
              return null;
            },
          ),

          const SizedBox(height: 8),

          // Password Strength Bar
          _buildPasswordStrengthBar(),

          const SizedBox(height: 12),

          // Field 4: Ulangi Kata Sandi
          AnimatedDopamineTextField(
            controller: _confirmPasswordController,
            label: 'Ulangi Kata Sandi',
            hintText: 'Konfirmasi kata sandi kamu',
            iconifySvg: CuteIconifyIcons.shieldCute,
            activeColor: const Color(0xFF8CE323),
            isPassword: true,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Konfirmasi sandi wajib diisi';
              }
              if (value != _passwordController.text) {
                return 'Kata sandi tidak cocok';
              }
              return null;
            },
          ),

          const SizedBox(height: 18),

          // CTA: Daftar Sekarang ->
          Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(AppRadius.pill),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF8CE323).withOpacity(0.42),
                  blurRadius: 18,
                  offset: const Offset(0, 7),
                ),
              ],
            ),
            child: ElevatedButton(
              onPressed: () {
                if (_formKey.currentState?.validate() ?? false) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Pendaftaran berhasil!'),
                      backgroundColor: AppColors.limeDeep,
                    ),
                  );
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFB5F438),
                foregroundColor: AppColors.darkSlate,
                padding: const EdgeInsets.symmetric(vertical: 15),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(AppRadius.pill),
                ),
                elevation: 0,
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: const [
                  Text(
                    'Daftar Sekarang',
                    style: TextStyle(
                      fontFamily: AppTypography.headlineFont,
                      fontSize: 15,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.2,
                    ),
                  ),
                  SizedBox(width: 8),
                  Icon(
                    Icons.arrow_forward_rounded,
                    size: 19,
                    color: AppColors.darkSlate,
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 18),

          // Divider ATAU
          Row(
            children: [
              Expanded(
                child: Container(
                  height: 1,
                  color: const Color(0xFFE5EBE0),
                ),
              ),
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 14),
                child: Text(
                  'ATAU',
                  style: TextStyle(
                    fontFamily: AppTypography.headlineFont,
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textMuted,
                    letterSpacing: 0.8,
                  ),
                ),
              ),
              Expanded(
                child: Container(
                  height: 1,
                  color: const Color(0xFFE5EBE0),
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Google Button
          Container(
            height: 50,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(AppRadius.pill),
              border: Border.all(
                color: const Color(0xFFE2E8DE),
                width: 1.2,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.02),
                  blurRadius: 6,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(AppRadius.pill),
                onTap: () {},
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: const [
                    Iconify(
                      CuteIconifyIcons.googleLogo,
                      size: 20,
                    ),
                    SizedBox(width: 12),
                    Text(
                      'Lanjutkan dengan Google',
                      style: TextStyle(
                        fontFamily: AppTypography.headlineFont,
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: AppColors.darkSlate,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          const SizedBox(height: 20),

          // Bottom switch link
          Wrap(
            alignment: WrapAlignment.center,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              const Text(
                'Sudah punya akun Progressio? ',
                style: TextStyle(
                  fontFamily: AppTypography.bodyFont,
                  fontSize: 12,
                  color: AppColors.textMuted,
                ),
              ),
              GestureDetector(
                onTap: widget.onSwitchToLogin,
                child: const Text(
                  'Masuk di Sini',
                  style: TextStyle(
                    fontFamily: AppTypography.headlineFont,
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    color: AppColors.lavenderPrimary,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPasswordStrengthBar() {
    final text = _passwordController.text;
    final strength = _calculatePasswordStrength(text);
    final color = _getStrengthColor(strength);
    final label = _getStrengthLabel(strength);

    return Row(
      children: [
        Expanded(
          child: Row(
            children: List.generate(3, (index) {
              final isFilled = text.isNotEmpty && index < strength;
              return Expanded(
                child: Container(
                  margin: EdgeInsets.only(right: index < 2 ? 6.0 : 0.0),
                  height: 4.5,
                  decoration: BoxDecoration(
                    color: isFilled ? color : const Color(0xFFE2E8DE),
                    borderRadius: BorderRadius.circular(3),
                  ),
                ),
              );
            }),
          ),
        ),
        const SizedBox(width: 14),
        Row(
          children: [
            const Text(
              'Kekuatan: ',
              style: TextStyle(
                fontFamily: AppTypography.bodyFont,
                fontSize: 11.5,
                color: AppColors.textMuted,
              ),
            ),
            Text(
              text.isEmpty ? '-' : label,
              style: TextStyle(
                fontFamily: AppTypography.headlineFont,
                fontSize: 11.5,
                fontWeight: FontWeight.w800,
                color: text.isEmpty ? AppColors.textMuted : color,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

/// ─────────────────────────────────────────────────────────────────────────────
/// RegisterPage Standalone Screen (untuk route mandiri bila dipanggil langsung)
/// ─────────────────────────────────────────────────────────────────────────────
class RegisterPage extends StatelessWidget {
  const RegisterPage({super.key});

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.of(context).size.height;

    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          // Header Image Lime with Gradient
          Positioned(
            top: -15,
            left: 0,
            right: 0,
            height: 460,
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Color(0xFFC7F37A),
                    Color(0xFFE8FCD0),
                    Colors.white,
                  ],
                  stops: [0.0, 0.65, 1.0],
                ),
              ),
              child: SafeArea(
                bottom: false,
                child: Center(
                  child: Builder(
                    builder: (context) {
                      final dpr = MediaQuery.of(context).devicePixelRatio;
                      final physicalSize = (460 * dpr).toInt();
                      return Image(
                        image: ResizeImage(
                          const AssetImage('assets/images/Hello_Login.png'),
                          width: physicalSize,
                          height: physicalSize,
                        ),
                        width: 460,
                        height: 460,
                        fit: BoxFit.contain,
                        filterQuality: FilterQuality.high,
                        isAntiAlias: true,
                      );
                    },
                  ),
                ),
              ),
            ),
          ),

          // Scrollable Content
          Positioned.fill(
            child: SingleChildScrollView(
              child: ConstrainedBox(
                constraints: BoxConstraints(
                  minHeight: screenHeight,
                ),
                // ponytail: IntrinsicHeight dihapus — double-pass layout mahal.
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    SizedBox(height: screenHeight * 0.35),
                      Container(
                        width: double.infinity,
                        decoration: const BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.only(
                            topLeft: Radius.circular(32),
                            topRight: Radius.circular(32),
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: Color(0x18000000),
                              blurRadius: 28,
                              offset: Offset(0, -6),
                            ),
                          ],
                        ),
                        padding: const EdgeInsets.fromLTRB(26, 16, 26, 32),
                        child: RegisterFormContent(
                          onSwitchToLogin: () {
                            Navigator.of(context).pop();
                          },
                        ),
                      ),
                    ],
                  ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
