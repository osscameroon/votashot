import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_form_builder/flutter_form_builder.dart';
import 'package:form_builder_image_picker/form_builder_image_picker.dart';
import 'package:mime/mime.dart';

import '../config/app_config.dart';
import '../l10n/app_localizations.dart';
import '../db/upload_stats_dao.dart';
import '../services/s3_uploader.dart';
import '../services/api_client.dart';
import '../state/session.dart';
import '../widgets/app_bottom_nav.dart';

/// Page to upload poll office list photos to S3 under `poll_office_list/`.
class PollOfficeListPage extends StatefulWidget {
  const PollOfficeListPage({super.key});

  @override
  State<PollOfficeListPage> createState() => _PollOfficeListPageState();
}

class _PollOfficeListPageState extends State<PollOfficeListPage> {
  final _formKey = GlobalKey<FormBuilderState>();
  bool _submitting = false;
  static const String _statKey = 'poll_office_list_sent';
  int _sentCount = 0;

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    final c = await UploadStatsDao.instance.getCount(_statKey);
    if (mounted) setState(() => _sentCount = c);
  }

  Future<void> _submit() async {
    final form = _formKey.currentState!;
    if (!form.saveAndValidate()) return;
    final images = (form.value['images'] as List?) ?? [];
    if (images.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(context.l10n.uploadNoImages)));
      return;
    }
    final s3 = Session.instance.s3;
    if (s3 == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(context.l10n.uploadMissingCreds)));
      return;
    }
    setState(() => _submitting = true);
    try {
      final uploader = S3Uploader();
      var creds = s3.credentials;
      var endpoint = creds.endpoint;

      int success = 0;
      int failed = 0;
      for (final item in images) {
        File? file;
        // Handle both File and cross_file's XFile without direct import.
        if (item is File) {
          file = item;
        } else if (item is dynamic && item.path is String) {
          file = File(item.path as String);
        }
        if (file == null) continue;
        final bytes = await file.readAsBytes();
        final name = file.path.split('/').last;
        final ct = lookupMimeType(file.path) ?? 'application/octet-stream';

        var result = await uploader.putToS3(
          endpoint: endpoint,
          region: creds.region,
          bucket: creds.bucket,
          objectKey: name,
          keyPrefix: '${creds.prefix}/poll_office_list',
          virtualHost: true,
          bytes: bytes,
          contentType: ct,
          accessKeyId: creds.accessKeyId,
          secretAccessKey: creds.secretAccessKey,
          sessionToken: creds.sessionToken.isEmpty ? null : creds.sessionToken,
        );
        if (result.statusCode == 401 || result.statusCode == 403) {
          try {
            final refreshed = await ApiClient.instance.refreshS3Credentials();
            creds = refreshed;
            endpoint = refreshed.endpoint;
            result = await uploader.putToS3(
              endpoint: endpoint,
              region: creds.region,
              bucket: creds.bucket,
              objectKey: name,
              keyPrefix: '${creds.prefix}/poll_office_list',
              virtualHost: true,
              bytes: bytes,
              contentType: ct,
              accessKeyId: creds.accessKeyId,
              secretAccessKey: creds.secretAccessKey,
              sessionToken: creds.sessionToken.isEmpty ? null : creds.sessionToken,
            );
          } catch (e) {
            // If refresh fails, treat as failure for this file
            result = S3PutResult(statusCode: 0, requestUrl: '');
          }
        }
        if (result.statusCode >= 200 && result.statusCode < 300) {
          success++;
        } else {
          failed++;
        }
      }
      if (!mounted) return;
      if (failed == 0 && success > 0) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(context.l10n.uploadSuccess),
            duration: const Duration(seconds: 10),
          ),
        );
        // Persist and reflect the number of images sent
        final newCount = await UploadStatsDao.instance.increment(_statKey, success);
        setState(() => _sentCount = newCount);
        form.reset();
        Navigator.of(context).pushReplacementNamed(AppRouter.homeRoute);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(context.l10n.uploadedFailedCount(failed, success + failed)),
            duration: const Duration(seconds: 10),
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('${context.l10n.uploadError}: $e')));
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(context.l10n.listTitle),
        automaticallyImplyLeading: false,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: FormBuilder(
          key: _formKey,
          child: Column(
            children: [
              Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  context.l10n.alreadySentCount(_sentCount),
                  style: Theme.of(context).textTheme.labelMedium,
                ),
              ),
              const SizedBox(height: 8),
              FormBuilderImagePicker(
                name: 'images',
                fit: BoxFit.cover,
                decoration: InputDecoration(
                  labelText: context.l10n.formPhotos,
                  border: const OutlineInputBorder(),
                ),
                maxImages: 20,
                availableImageSources: const [ImageSourceOption.gallery],
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _submitting ? null : _submit,
                  icon: _submitting
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.cloud_upload),
                  label: Text(context.l10n.submit),
                ),
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: const AppBottomNav(currentIndex: 0),
    );
  }
}
