# SitePopup

`SitePopup` is the admin-managed homepage announcement modal used for college-wide notices.

## Fields

- `title`: announcement headline
- `message`: announcement body text
- `image`: optional banner image stored under `popups/`
- `button_text`: CTA label shown on the popup button
- `button_url`: target URL for the CTA
- `is_active`: master on/off switch
- `start_date`: optional publish window start
- `end_date`: optional publish window end
- `display_order`: lower numbers appear first when multiple popups qualify
- `created_at` / `updated_at`: audit timestamps

## Admin usage

- Create or edit popups in the Django admin under `Site popups`
- Use the image preview to confirm the uploaded asset
- Keep only one popup active when you want a single announcement shown on the homepage

## Activation rules

- A popup is eligible only when `is_active` is enabled
- If `start_date` is set, the current time must be on or after that value
- If `end_date` is set, the current time must be on or before that value
- If more than one popup qualifies, the one with the lowest `display_order` is used

## Scheduling

- Leave `start_date` and `end_date` blank for immediate unscheduled use
- Set both dates to run time-limited announcements such as admissions, screening, matriculation, accreditation, application calls, notices, or emergency alerts

## Images

- Uploading an image is optional
- Images use the existing media storage configuration in development and production
- Use a clear title because it becomes the image alt text on the homepage
