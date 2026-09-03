import 'package:flutter/material.dart';
import 'package:iconify_flutter/iconify_flutter.dart';
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_spacing.dart';
import 'package:progressio_mobile/core/constants/app_typography.dart';
import 'package:progressio_mobile/core/constants/cute_iconify_icons.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// AnimatedDopamineTextField — Floating Label cut-out border pill
/// Label melayang mulus ke atas memotong border saat fokus atau terisi teks.
/// ─────────────────────────────────────────────────────────────────────────────
class AnimatedDopamineTextField extends StatefulWidget {
  final TextEditingController controller;
  final String label;
  final String hintText;
  final String? iconifySvg;
  final IconData? prefixIcon;
  final Color activeColor;
  final bool isPassword;
  final TextInputType keyboardType;
  final String? Function(String?)? validator;

  const AnimatedDopamineTextField({
    super.key,
    required this.controller,
    required this.label,
    required this.hintText,
    this.iconifySvg,
    this.prefixIcon,
    this.activeColor = AppColors.lavenderPrimary,
    this.isPassword = false,
    this.keyboardType = TextInputType.text,
    this.validator,
  });

  @override
  State<AnimatedDopamineTextField> createState() => _AnimatedDopamineTextFieldState();
}

class _AnimatedDopamineTextFieldState extends State<AnimatedDopamineTextField>
    with SingleTickerProviderStateMixin {
  final FocusNode _focusNode = FocusNode();
  bool _isFocused = false;
  bool _obscureText = true;

  late final AnimationController _eyeAnimController;
  late final Animation<double> _eyeScaleAnimation;
  late final Animation<double> _eyeRotationAnimation;

  @override
  void initState() {
    super.initState();
    _eyeAnimController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 380),
    );

    // Animasi membal kenyal (fluid jelly squash & stretch)
    _eyeScaleAnimation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.0, end: 0.70)
            .chain(CurveTween(curve: Curves.easeInQuad)),
        weight: 30,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 0.70, end: 1.25)
            .chain(CurveTween(curve: Curves.easeOutBack)),
        weight: 45,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.25, end: 1.0)
            .chain(CurveTween(curve: Curves.elasticOut)),
        weight: 25,
      ),
    ]).animate(_eyeAnimController);

    // Rotasi sedikit dinamis saat mata berkedip / terbuka
    _eyeRotationAnimation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween<double>(begin: 0.0, end: -0.12)
            .chain(CurveTween(curve: Curves.easeOutQuad)),
        weight: 35,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: -0.12, end: 0.08)
            .chain(CurveTween(curve: Curves.easeInOutQuad)),
        weight: 35,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 0.08, end: 0.0)
            .chain(CurveTween(curve: Curves.elasticOut)),
        weight: 30,
      ),
    ]).animate(_eyeAnimController);

    _focusNode.addListener(() {
      setState(() {
        _isFocused = _focusNode.hasFocus;
      });
    });
    widget.controller.addListener(() {
      if (mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    _eyeAnimController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bool hasText = widget.controller.text.isNotEmpty;
    final bool isFloated = _isFocused || hasText;

    return Theme(
      data: Theme.of(context).copyWith(
        colorScheme: Theme.of(context).colorScheme.copyWith(
          primary: widget.activeColor,
        ),
      ),
      child: TextFormField(
        controller: widget.controller,
        focusNode: _focusNode,
        keyboardType: widget.keyboardType,
        obscureText: widget.isPassword ? _obscureText : false,
        validator: widget.validator,
        style: const TextStyle(
          fontFamily: AppTypography.bodyFont,
          fontSize: 14,
          fontWeight: FontWeight.w500,
          color: AppColors.textMain,
        ),
        decoration: InputDecoration(
          labelText: widget.label,
          labelStyle: TextStyle(
            fontFamily: AppTypography.headlineFont,
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: _isFocused ? widget.activeColor : AppColors.textMuted,
          ),
          floatingLabelStyle: TextStyle(
            fontFamily: AppTypography.headlineFont,
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: _isFocused ? widget.activeColor : AppColors.textMuted,
          ),
          floatingLabelBehavior: FloatingLabelBehavior.auto,
          hintText: isFloated ? widget.hintText : null,
          hintStyle: const TextStyle(
            color: AppColors.textMuted,
            fontSize: 13,
          ),
          filled: true,
          fillColor: Colors.white,
          prefixIcon: Padding(
            padding: const EdgeInsets.only(left: 18, right: 12),
            child: widget.iconifySvg != null
                ? Iconify(
                    widget.iconifySvg!,
                    color: _isFocused ? widget.activeColor : (hasText ? AppColors.textMain : AppColors.textMuted),
                    size: 21,
                  )
                : Icon(
                    widget.prefixIcon ?? Icons.star,
                    color: _isFocused ? widget.activeColor : (hasText ? AppColors.textMain : AppColors.textMuted),
                    size: 20,
                  ),
          ),
          prefixIconConstraints: const BoxConstraints(
            minWidth: 52,
            minHeight: 24,
          ),
          suffixIcon: widget.isPassword
              ? Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: IconButton(
                    iconSize: 22,
                    splashRadius: 20,
                    constraints: const BoxConstraints(
                      minWidth: 40,
                      minHeight: 40,
                    ),
                    icon: AnimatedBuilder(
                      animation: _eyeAnimController,
                      builder: (context, child) {
                        return Transform.rotate(
                          angle: _eyeRotationAnimation.value,
                          child: Transform.scale(
                            scale: _eyeScaleAnimation.value,
                            child: AnimatedSwitcher(
                              duration: const Duration(milliseconds: 200),
                              transitionBuilder: (child, anim) => FadeTransition(
                                opacity: anim,
                                child: ScaleTransition(
                                  scale: anim,
                                  child: child,
                                ),
                              ),
                              child: _obscureText
                                  ? Iconify(
                                      CuteIconifyIcons.eyeCute,
                                      key: const ValueKey<bool>(true),
                                      color: _isFocused ? widget.activeColor : AppColors.textMuted,
                                      size: 20,
                                    )
                                  : Iconify(
                                      CuteIconifyIcons.eyeClosedCute,
                                      key: const ValueKey<bool>(false),
                                      color: _isFocused ? widget.activeColor : AppColors.textMuted,
                                      size: 20,
                                    ),
                            ),
                          ),
                        );
                      },
                    ),
                    onPressed: () {
                      _eyeAnimController.forward(from: 0.0);
                      setState(() {
                        _obscureText = !_obscureText;
                      });
                    },
                  ),
                )
              : null,
          suffixIconConstraints: const BoxConstraints(
            minWidth: 48,
            minHeight: 48,
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 20,
            vertical: 15,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppRadius.pill),
            borderSide: const BorderSide(
              color: Color(0xFFE2E8DE),
              width: 1.5,
            ),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppRadius.pill),
            borderSide: const BorderSide(
              color: Color(0xFFE2E8DE),
              width: 1.5,
            ),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppRadius.pill),
            borderSide: BorderSide(
              color: widget.activeColor,
              width: 2.0,
            ),
          ),
          errorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppRadius.pill),
            borderSide: const BorderSide(
              color: AppColors.heartRed,
              width: 1.5,
            ),
          ),
          focusedErrorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppRadius.pill),
            borderSide: const BorderSide(
              color: AppColors.heartRed,
              width: 2.0,
            ),
          ),
        ),
      ),
    );
  }
}
