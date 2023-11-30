/*Daily - BOM - CoSo*/

/*Headline Tag - Fee Income (Phần trăm hoàn thành chỉ tiêu ngày - Phí giao dịch) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @Prev DATETIME;
SET @Prev = (
	SELECT MIN([Date]) 
	FROM (
		SELECT TOP 2 
			[Date]
		FROM [Date]
		WHERE [Work] = 1
			AND [Date] <= @Date
		ORDER BY [Date] DESC
	) [z]
);

WITH 

[TargetByBranch] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'Fee Income'
)

, [PrevValue] AS (
	SELECT
		ISNULL(SUM([trading_record].[fee]), 0) [FeeIncome]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] = @Prev
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
)

, [TodayValue] AS (
	SELECT
		ISNULL(SUM([trading_record].[fee]), 0) [FeeIncome]
	FROM [trading_record]
	LEFT JOIN [relationship]
		ON [relationship].[sub_account] = [trading_record].[sub_account]
		AND [relationship].[date] = [trading_record].[date]
	WHERE [trading_record].[date] = @Date
		AND [relationship].[branch_id] IN (SELECT [BranchID] FROM [TargetByBranch])
		AND [trading_record].[type_of_asset] NOT IN (N'Trái phiếu doanh nghiệp', N'Trái phiếu', N'Trái phiếu chính phủ')
		AND [relationship].[account_code] NOT LIKE '022P%'
)

SELECT
	[TodayValue].[FeeInCome] [FeeIncome]
	, [TodayValue].[FeeInCome] - [PrevValue].[FeeInCome] [AbsoluteChange]
	, CASE 
		WHEN [PrevValue].[FeeInCome] = 0 THEN 0
		ELSE [TodayValue].[FeeInCome] / [PrevValue].[FeeInCome] - 1
	END [RelativeChange]
FROM [PrevValue]
CROSS JOIN [TodayValue]


END
