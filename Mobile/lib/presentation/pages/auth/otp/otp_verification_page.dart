import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:iconify_flutter/iconify_flutter.dart';
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_spacing.dart';
import 'package:progressio_mobile/core/constants/app_typography.dart';
import 'package:progressio_mobile/core/constants/cute_iconify_icons.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// OtpVerificationPage — Halaman Verifikasi OTP
/// - Full putih murni (tanpa karakter ilustrasi dan tanpa clue instruksi rumit).
/// - Mengikuti Neo-Dopamine Design System (DESIGN.md):
///   * High Contrast & Tactile Pill Geometry.
///   * Input 6 digit interaktif dengan auto-focus ke digit berikutnya & backspace support.
///   * Timer hitung mundur resend code dengan aksen Dopamine.
/// ─────────────────────────────────────────────────────────────────────────────
class OtpVerificationPage extends StatefulWidget {
  final String email;

  const OtpVerificationPage({
    super.key,
    this.email = 'learner.code@progressio.id',
  });

  static const String routePath = '/auth/otp-verification';

  @override
  State<OtpVerificationPage> createState() => _OtpVerificationPageState();
}

class _OtpVerificationPageState extends State<OtpVerificationPage>
    with SingleTickerProviderStateMixin {
  static const int _otpLength = 6;
  static const int _initialTimerSeconds = 60;

  final List<TextEditingController> _controllers =
      List.generate(_otpLength, (_) => TextEditingController());
  final List<FocusNode> _focusNodes =
      List.generate(_otpLength, (_) => FocusNode());

  late final AnimationController _animController;
  late final Animation<Offset> _slideAnimation;
  late final Animation<double> _fadeAnimation;

  Timer? _timer;
  int _secondsRemaining = _initialTimerSeconds;
  bool _canResend = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _startTimer();

    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 550),
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0.0, 0.08),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _animController,
        curve: Curves.easeOutCubic,
      ),
    );

    _fadeAnimation = CurvedAnimation(
      parent: _animController,
      curve: const Interval(0.0, 0.9, curve: Curves.easeOut),
    );

    _animController.forward();

    // Auto focus kotak pertama setelah build selesai
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted && _focusNodes.isNotEmpty) {
        _focusNodes[0].requestFocus();
      }
    });
  }

  void _startTimer() {
    setState(() {
      _secondsRemaining = _initialTimerSeconds;
      _canResend = false;
    });
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_secondsRemaining > 0) {
        setState(() => _secondsRemaining--);
      } else {
        _timer?.cancel();
        setState(() => _canResend = true);
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _animController.dispose();
    for (final c in _controllers) {
      c.dispose();
    }
    for (final f in _focusNodes) {
      f.dispose();
    }
    super.dispose();
  }

  String get _currentOtp => _controllers.map((c) => c.text).join();

  void _onOtpDigitChanged(String value, int index) {
    if (value.length > 1) {
      // Handle jika user paste multi-digit
      final digits = value.replaceAll(RegExp(r'[^0-9]'), '');
      for (int i = 0; i < _otpLength; i++) {
        if (i < digits.length) {
          _controllers[i].text = digits[i];
        }
      }
      final nextIndex = digits.length < _otpLength ? digits.length : _otpLength - 1;
      _focusNodes[nextIndex].requestFocus();
      setState(() {});
      if (digits.length >= _otpLength) {
        _handleVerifyOtp();
      }
      return;
    }

    if (value.isNotEmpty) {
      if (index < _otpLength - 1) {
        _focusNodes[index + 1].requestFocus();
      } else {
        _focusNodes[index].unfocus();
        if (_currentOtp.length == _otpLength) {
          _handleVerifyOtp();
        }
      }
    }
    setState(() {});
  }

  void _handleResendCode() {
    if (!_canResend || _isLoading) return;

    for (final c in _controllers) {
      c.clear();
    }
    _focusNodes[0].requestFocus();
    _startTimer();

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: AppColors.darkSlate,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.card),
        ),
        content: Row(
          children: const [
            Text('✨', style: TextStyle(fontSize: 18)),
            SizedBox(width: 8),
            Expanded(
              child: Text(
                'Kode verifikasi baru telah dikirimkan ke email kamu!',
                style: TextStyle(
                  fontFamily: AppTypography.headlineFont,
                  fontWeight: FontWeight.w600,
                  color: AppColors.limePrimary,
                  fontSize: 13,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _handleVerifyOtp() {
    final otp = _currentOtp;
    if (otp.length < _otpLength) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: AppColors.heartRed,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.card),
          ),
          content: const Text(
            'Masukkan 6 digit kode OTP lengkap',
            style: TextStyle(
              fontFamily: AppTypography.headlineFont,
              fontWeight: FontWeight.w600,
              color: Colors.white,
              fontSize: 13,
            ),
          ),
        ),
      );
      return;
    }

    setState(() => _isLoading = true);

    Future.delayed(const Duration(milliseconds: 900), () {
      if (!mounted) return;
      setState(() => _isLoading = false);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: AppColors.darkSlate,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.card),
          ),
          content: Row(
            children: const [
              Text('🎉', style: TextStyle(fontSize: 18)),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Verifikasi berhasil! Akun kamu telah aktif.',
                  style: TextStyle(
                    fontFamily: AppTypography.headlineFont,
                    fontWeight: FontWeight.w600,
                    color: AppColors.limePrimary,
                    fontSize: 13,
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final isOtpComplete = _currentOtp.length == _otpLength;

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            // Top Bar: Tombol Kembali
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              child: Row(
                children: [
                  Material(
                    color: Colors.transparent,
                    child: InkWell(
                      onTap: () => Navigator.of(context).maybePop(),
                      borderRadius: BorderRadius.circular(999),
                      child: Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: const Color(0xFFF8FAFC),
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: const Color(0xFFE2E8F0),
                            width: 1,
                          ),
                        ),
                        child: const Icon(
                          Icons.arrow_back_rounded,
                          color: AppColors.textMain,
                          size: 20,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Konten Utama
            Expanded(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: FadeTransition(
                  opacity: _fadeAnimation,
                  child: SlideTransition(
                    position: _slideAnimation,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 20),

                        // Icon Header Dopamine Badge
                        Container(
                          width: 52,
                          height: 52,
                          decoration: BoxDecoration(
                            color: const Color(0xFFEDE6FF),
                            borderRadius: BorderRadius.circular(AppRadius.card),
                            border: Border.all(
                              color: const Color(0xFFDDD3FF),
                              width: 1.5,
                            ),
                          ),
                          child: const Center(
                            child: Iconify(
                              CuteIconifyIcons.shieldCute,
                              size: 26,
                              color: AppColors.lavenderPrimary,
                            ),
                          ),
                        ),
                        const SizedBox(height: 20),

                        // Judul Halaman
                        const Text(
                          'Verifikasi Kode OTP ✉️',
                          style: TextStyle(
                            fontFamily: AppTypography.headlineFont,
                            fontSize: 26,
                            fontWeight: FontWeight.w800,
                            color: AppColors.textMain,
                            letterSpacing: -0.5,
                          ),
                        ),
                        const SizedBox(height: 10),

                        // Deskripsi Email Penerima
                        RichText(
                          text: TextSpan(
                            style: const TextStyle(
                              fontFamily: AppTypography.bodyFont,
                              fontSize: 14,
                              color: Color(0xFF64748B),
                              fontWeight: FontWeight.w500,
                              height: 1.45,
                            ),
                            children: [
                              const TextSpan(
                                text: 'Masukkan 6 digit kode yang telah kami kirimkan ke ',
                              ),
                              TextSpan(
                                text: widget.email,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.textMain,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 36),

                        // OTP Input Boxes (6 Digit)
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: List.generate(_otpLength, (index) {
                            return _buildOtpBox(index);
                          }),
                        ),
                        const SizedBox(height: 32),

                        // Tombol Aksi Verifikasi
                        Container(
                          height: 52,
                          width: double.infinity,
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(AppRadius.pill),
                            boxShadow: isOtpComplete
                                ? [
                                    BoxShadow(
                                      color: const Color(0xFFB5F942).withValues(alpha: 0.5),
                                      blurRadius: 18,
                                      offset: const Offset(0, 6),
                                    ),
                                  ]
                                : [],
                          ),
                          child: ElevatedButton(
                            onPressed: (_isLoading || !isOtpComplete)
                                ? null
                                : _handleVerifyOtp,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFFB8F846),
                              disabledBackgroundColor: const Color(0xFFE2E8DE),
                              foregroundColor: AppColors.darkSlate,
                              disabledForegroundColor: const Color(0xFF94A3B8),
                              elevation: 0,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(AppRadius.pill),
                              ),
                            ),
                            child: _isLoading
                                ? const SizedBox(
                                    width: 22,
                                    height: 22,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2.5,
                                      color: AppColors.darkSlate,
                                    ),
                                  )
                                : Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: const [
                                      Text(
                                        'Verifikasi Sekarang',
                                        style: TextStyle(
                                          fontFamily: AppTypography.headlineFont,
                                          fontSize: 15,
                                          fontWeight: FontWeight.w800,
                                          color: AppColors.darkSlate,
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
                        const SizedBox(height: 28),

                        // Resend OTP & Countdown Timer
                        Center(
                          child: _canResend
                              ? Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    const Text(
                                      'Tidak menerima kode? ',
                                      style: TextStyle(
                                        fontFamily: AppTypography.bodyFont,
                                        fontSize: 13,
                                        color: Color(0xFF64748B),
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                    GestureDetector(
                                      onTap: _handleResendCode,
                                      child: const Text(
                                        'Kirim Ulang',
                                        style: TextStyle(
                                          fontFamily: AppTypography.headlineFont,
                                          fontSize: 13,
                                          fontWeight: FontWeight.w800,
                                          color: AppColors.lavenderPrimary,
                                        ),
                                      ),
                                    ),
                                  ],
                                )
                              : Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 16,
                                    vertical: 8,
                                  ),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF8FAFC),
                                    borderRadius: BorderRadius.circular(AppRadius.pill),
                                    border: Border.all(
                                      color: const Color(0xFFE2E8F0),
                                      width: 1,
                                    ),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Icon(
                                        Icons.timer_outlined,
                                        size: 16,
                                        color: Color(0xFF64748B),
                                      ),
                                      const SizedBox(width: 6),
                                      Text(
                                        'Kirim ulang dalam ${_secondsRemaining.toString().padLeft(2, '0')}s',
                                        style: const TextStyle(
                                          fontFamily: AppTypography.headlineFont,
                                          fontSize: 13,
                                          fontWeight: FontWeight.w700,
                                          color: Color(0xFF64748B),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                        ),
                        const SizedBox(height: 24),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOtpBox(int index) {
    final controller = _controllers[index];
    final focusNode = _focusNodes[index];
    final hasValue = controller.text.isNotEmpty;
    final isFocused = focusNode.hasFocus;

    return Focus(
      onKeyEvent: (node, event) {
        if (event is KeyDownEvent &&
            event.logicalKey == LogicalKeyboardKey.backspace &&
            controller.text.isEmpty &&
            index > 0) {
          _focusNodes[index - 1].requestFocus();
          _controllers[index - 1].clear();
          setState(() {});
          return KeyEventResult.handled;
        }
        return KeyEventResult.ignored;
      },
      child: Container(
        width: 48,
        height: 58,
        decoration: BoxDecoration(
          color: isFocused
              ? Colors.white
              : (hasValue ? const Color(0xFFF5FDF0) : const Color(0xFFF6F8F6)),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isFocused
                ? AppColors.lavenderPrimary
                : (hasValue ? const Color(0xFF8DE319) : const Color(0xFFE5EAE5)),
            width: isFocused ? 2.0 : 1.2,
          ),
          boxShadow: isFocused
              ? [
                  BoxShadow(
                    color: AppColors.lavenderPrimary.withValues(alpha: 0.18),
                    blurRadius: 10,
                    offset: const Offset(0, 2),
                  ),
                ]
              : null,
        ),
        child: Center(
          child: TextFormField(
            controller: controller,
            focusNode: focusNode,
            keyboardType: TextInputType.number,
            textAlign: TextAlign.center,
            maxLength: 1,
            style: const TextStyle(
              fontFamily: AppTypography.headlineFont,
              fontSize: 22,
              fontWeight: FontWeight.w800,
              color: AppColors.textMain,
            ),
            inputFormatters: [
              FilteringTextInputFormatter.digitsOnly,
            ],
            decoration: const InputDecoration(
              counterText: '',
              border: InputBorder.none,
              contentPadding: EdgeInsets.zero,
            ),
            onChanged: (value) => _onOtpDigitChanged(value, index),
          ),
        ),
      ),
    );
  }
}
