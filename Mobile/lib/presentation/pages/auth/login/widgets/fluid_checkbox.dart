import 'package:flutter/material.dart';
import 'package:progressio_mobile/core/constants/app_colors.dart';
import 'package:progressio_mobile/core/constants/app_typography.dart';

/// ─────────────────────────────────────────────────────────────────────────────
/// FluidDopamineCheckbox — Checkbox dengan animasi cairan memantul (fluid pop)
/// serta coretan centang yang digambar dinamis dan mulus.
/// ─────────────────────────────────────────────────────────────────────────────
class FluidDopamineCheckbox extends StatefulWidget {
  final bool value;
  final ValueChanged<bool> onChanged;
  final String label;
  final Color activeColor;

  const FluidDopamineCheckbox({
    super.key,
    required this.value,
    required this.onChanged,
    required this.label,
    this.activeColor = const Color(0xFF8CE323),
  });

  @override
  State<FluidDopamineCheckbox> createState() => _FluidDopamineCheckboxState();
}

class _FluidDopamineCheckboxState extends State<FluidDopamineCheckbox>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _scaleAnimation;
  late final Animation<double> _checkProgress;
  late final Animation<double> _fluidRipple;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );

    // Animasi squash & stretch cairan (fluid bounce)
    _scaleAnimation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.0, end: 0.82)
            .chain(CurveTween(curve: Curves.easeOutQuad)),
        weight: 25,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 0.82, end: 1.20)
            .chain(CurveTween(curve: Curves.easeOutBack)),
        weight: 45,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.20, end: 1.0)
            .chain(CurveTween(curve: Curves.elasticOut)),
        weight: 30,
      ),
    ]).animate(_controller);

    // Animasi menggambar garis centang dari kiri ke kanan (stroke draw)
    _checkProgress = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.35, 1.0, curve: Curves.easeOutCubic),
    );

    // Efek ripple air di sekeliling saat 'centing'
    _fluidRipple = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.1, 0.7, curve: Curves.easeOutQuad),
    );

    if (widget.value) {
      _controller.value = 1.0;
    }
  }

  @override
  void didUpdateWidget(FluidDopamineCheckbox oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.value != oldWidget.value) {
      if (widget.value) {
        _controller.forward(from: 0.0);
      } else {
        _controller.reverse();
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: () {
        widget.onChanged(!widget.value);
      },
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              return Stack(
                alignment: Alignment.center,
                clipBehavior: Clip.none,
                children: [
                  // Fluid splash ring yang memancar keluar saat di-klik
                  if (_fluidRipple.value > 0 && _fluidRipple.value < 1.0)
                    Transform.scale(
                      scale: 1.0 + (_fluidRipple.value * 0.8),
                      child: Container(
                        width: 22,
                        height: 22,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: widget.activeColor.withOpacity(
                              (1.0 - _fluidRipple.value) * 0.6,
                            ),
                            width: 2.5,
                          ),
                        ),
                      ),
                    ),

                  // Box Checkbox dengan Fluid Scale
                  Transform.scale(
                    scale: _scaleAnimation.value,
                    child: Container(
                      width: 22,
                      height: 22,
                      decoration: BoxDecoration(
                        color: Color.lerp(
                          Colors.white,
                          widget.activeColor,
                          _controller.value,
                        ),
                        borderRadius: BorderRadius.circular(
                          // Sedikit membulat saat memantul (liquid jelly feeling)
                          7.0 + (_scaleAnimation.value > 1.0 ? 2.5 : 0.0),
                        ),
                        border: Border.all(
                          color: Color.lerp(
                            const Color(0xFFD4DED0),
                            widget.activeColor,
                            _controller.value,
                          )!,
                          width: 1.8,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: widget.activeColor.withOpacity(
                              _controller.value * 0.40,
                            ),
                            blurRadius: 8 * _controller.value,
                            offset: Offset(0, 2 * _controller.value),
                          ),
                        ],
                      ),
                      child: CustomPaint(
                        painter: _FluidCheckPainter(
                          progress: _checkProgress.value,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
          const SizedBox(width: 9),
          Text(
            widget.label,
            style: TextStyle(
              fontFamily: AppTypography.bodyFont,
              fontSize: 12.5,
              fontWeight: widget.value ? FontWeight.w700 : FontWeight.w500,
              color: widget.value ? AppColors.darkSlate : AppColors.textMain,
            ),
          ),
        ],
      ),
    );
  }
}

/// Painter untuk menggambar garis centang secara mulus & fluid dari kiri ke kanan
class _FluidCheckPainter extends CustomPainter {
  final double progress;
  final Color color;

  _FluidCheckPainter({
    required this.progress,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (progress <= 0.01) return;

    final paint = Paint()
      ..color = color
      ..strokeWidth = 2.4
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..style = PaintingStyle.stroke;

    final p1 = Offset(size.width * 0.26, size.height * 0.52);
    final p2 = Offset(size.width * 0.44, size.height * 0.72);
    final p3 = Offset(size.width * 0.74, size.height * 0.32);

    final path = Path();
    path.moveTo(p1.dx, p1.dy);

    // Titik tengah pertama (garis pendek ke bawah)
    if (progress < 0.4) {
      final subT = progress / 0.4;
      path.lineTo(
        p1.dx + (p2.dx - p1.dx) * subT,
        p1.dy + (p2.dy - p1.dy) * subT,
      );
    } else {
      path.lineTo(p2.dx, p2.dy);
      // Garis panjang melesat ke atas
      final subT = (progress - 0.4) / 0.6;
      path.lineTo(
        p2.dx + (p3.dx - p2.dx) * subT,
        p2.dy + (p3.dy - p2.dy) * subT,
      );
    }

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _FluidCheckPainter oldDelegate) {
    return oldDelegate.progress != progress || oldDelegate.color != color;
  }
}
